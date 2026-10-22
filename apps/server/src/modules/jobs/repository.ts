import type { Job } from '@vanguard/contracts';
import { and, desc, eq } from 'drizzle-orm';
import { jobs, type JobRow } from '../../db/schema.ts';
import { getDrizzle } from '../../lib/db.ts';

function mapJob(row: JobRow): Job {
  return {
    id: row.id,
    user_id: row.user_id,
    task_id: row.task_id,
    source_url: row.source_url,
    title: row.title,
    company: row.company,
    location: row.location,
    description: row.description,
    created_at: new Date(row.created_at).toISOString(),
  };
}

export async function insertJob(input: {
  userId: string;
  taskId?: string | null;
  sourceUrl: string;
  title: string;
  company?: string | null;
  location?: string | null;
  description?: string | null;
}): Promise<Job> {
  const rows = await getDrizzle()
    .insert(jobs)
    .values({
      user_id: input.userId,
      task_id: input.taskId ?? null,
      source_url: input.sourceUrl,
      title: input.title,
      company: input.company ?? null,
      location: input.location ?? null,
      description: input.description ?? null,
    })
    .returning();
  const row = rows[0];
  if (!row) throw new Error('Failed to insert job');
  return mapJob(row);
}

export async function listJobs(userId: string, limit = 100): Promise<Job[]> {
  const rows = await getDrizzle()
    .select()
    .from(jobs)
    .where(eq(jobs.user_id, userId))
    .orderBy(desc(jobs.created_at))
    .limit(limit);
  return rows.map(mapJob);
}

export async function listJobsByTask(userId: string, taskId: string): Promise<Job[]> {
  const rows = await getDrizzle()
    .select()
    .from(jobs)
    .where(and(eq(jobs.user_id, userId), eq(jobs.task_id, taskId)))
    .orderBy(desc(jobs.created_at));
  return rows.map(mapJob);
}
