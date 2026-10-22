import type { Job } from '@vanguard/contracts';
import { getDb } from '../../lib/db.ts';

interface JobRow {
  id: string;
  user_id: string;
  task_id: string | null;
  source_url: string;
  title: string;
  company: string | null;
  location: string | null;
  description: string | null;
  created_at: Date;
}

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
  const sql = getDb();
  const rows = await sql<JobRow[]>`
    insert into public.jobs (user_id, task_id, source_url, title, company, location, description)
    values (
      ${input.userId},
      ${input.taskId ?? null},
      ${input.sourceUrl},
      ${input.title},
      ${input.company ?? null},
      ${input.location ?? null},
      ${input.description ?? null}
    )
    returning *
  `;
  const row = rows[0];
  if (!row) throw new Error('Failed to insert job');
  return mapJob(row);
}

export async function listJobs(userId: string, limit = 100): Promise<Job[]> {
  const sql = getDb();
  const rows = await sql<JobRow[]>`
    select * from public.jobs
     where user_id = ${userId}
     order by created_at desc
     limit ${limit}
  `;
  return rows.map(mapJob);
}

export async function listJobsByTask(userId: string, taskId: string): Promise<Job[]> {
  const sql = getDb();
  const rows = await sql<JobRow[]>`
    select * from public.jobs
     where user_id = ${userId} and task_id = ${taskId}
     order by created_at desc
  `;
  return rows.map(mapJob);
}
