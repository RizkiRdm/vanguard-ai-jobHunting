import { randomUUID } from 'node:crypto';
import { afterAll, beforeAll, describe, expect, it } from 'vitest';
import { closeDb, getDb } from '../../lib/db.ts';
import {
  approveTask,
  cancelTask,
  claimNextTask,
  finishTask,
  heartbeatTask,
  insertTask,
  findTask,
  listTasks,
  resumeTask,
} from '../tasks/repository.ts';
import { insertJob, listJobsByTask } from '../jobs/repository.ts';
import { ensureUserRow, getProfile, upsertProfile } from '../profile/repository.ts';
import { runMigrations } from '../../scripts/migrate.ts';

/**
 * Integration test for the SQL layer: ownership filters, atomic claiming, lease
 * guards and the approval flow. Needs a migrated Postgres with the Supabase auth
 * and storage objects present (see supabase/local-stub.sql), so it only runs when
 * TEST_DATABASE_URL is set.
 */
const databaseUrl = process.env.TEST_DATABASE_URL;
const suite = databaseUrl ? describe : describe.skip;

suite('task queue and repositories against Postgres', () => {
  const userA = randomUUID();
  const userB = randomUUID();

  beforeAll(async () => {
    process.env.DATABASE_URL = databaseUrl;
    process.env.SUPABASE_URL ??= 'https://test.supabase.co';
    process.env.SUPABASE_PUBLISHABLE_KEY ??= 'test';
    process.env.SUPABASE_SECRET_KEY ??= 'test';
    process.env.GEMINI_API_KEY ??= 'test';

    const sql = getDb();
    await runMigrations();
    for (const [id, email] of [
      [userA, 'a@example.com'],
      [userB, 'b@example.com'],
    ] as const) {
      await sql`insert into auth.users (id, email) values (${id}, ${email}) on conflict do nothing`;
      await ensureUserRow(id, email);
    }
  });

  afterAll(async () => {
    const sql = getDb();
    await sql`delete from public.tasks where user_id in (${userA}, ${userB})`;
    await sql`delete from public.user_profiles where user_id in (${userA}, ${userB})`;
    await sql`delete from public.llm_usage_log where user_id in (${userA}, ${userB})`;
    await sql`delete from public.budget_counters where user_id in (${userA}, ${userB})`;
    await sql`delete from public.users where id in (${userA}, ${userB})`;
    await sql`delete from auth.users where id in (${userA}, ${userB})`;
    await closeDb();
  });

  it('claims a task once and only for its owner', async () => {
    const created = await insertTask({
      userId: userA,
      type: 'discover',
      payload: { query: 'rust' },
    });

    expect(await findTask(userB, created.id)).toBeNull();
    expect((await listTasks(userB)).some((task) => task.id === created.id)).toBe(false);

    const claimed = await claimNextTask('worker-test', 60);
    expect(claimed?.id).toBe(created.id);
    expect(claimed?.attempts).toBe(1);

    const others = await claimNextTask('worker-other', 60);
    expect(others?.id).not.toBe(created.id);

    expect(await heartbeatTask(created.id, 'worker-other', 60)).toBe(false);
    expect(await heartbeatTask(created.id, 'worker-test', 60)).toBe(true);
    expect(
      await finishTask({ taskId: created.id, workerId: 'worker-other', status: 'succeeded' }),
    ).toBe(false);
    expect(
      await finishTask({ taskId: created.id, workerId: 'worker-test', status: 'succeeded' }),
    ).toBe(true);
  });

  it('records approval for the owner only', async () => {
    const task = await insertTask({ userId: userA, type: 'apply', payload: {} });
    await claimNextTask('worker-test', 60);
    await cancelTask(task.id, userA); // release the lease before parking another task
    const parked = await insertTask({ userId: userA, type: 'apply', payload: {} });
    expect((await claimNextTask('worker-test', 60))?.id).toBe(parked.id);

    expect(await approveTask(parked.id, userB)).toBe(false);
    expect(await cancelTask(parked.id, userB)).toBe(false);
    expect(await cancelTask(parked.id, userA)).toBe(true);
    expect(await resumeTask(parked.id, userA, { answer: 'x' })).toBe(false);
  });

  it('keeps jobs scoped to their owner', async () => {
    const task = await insertTask({ userId: userA, type: 'discover', payload: {} });
    const job = await insertJob({
      userId: userA,
      taskId: task.id,
      sourceUrl: 'https://example.com/jobs/1',
      title: 'Rust Developer',
    });

    expect(job.title).toBe('Rust Developer');
    expect((await listJobsByTask(userA, task.id)).map((row) => row.id)).toEqual([job.id]);
    expect(await listJobsByTask(userB, task.id)).toEqual([]);
  });

  it('upserts a profile and clears an emptied field', async () => {
    const saved = await upsertProfile(userA, {
      full_name: 'Ada',
      summary: 'Systems',
      skills: ['rust'],
    });
    expect(saved.skills).toEqual(['rust']);

    const cleared = await upsertProfile(userA, { full_name: 'Ada', skills: [] });
    expect(cleared.summary).toBeNull();
    expect((await getProfile(userA))?.full_name).toBe('Ada');
  });
});
