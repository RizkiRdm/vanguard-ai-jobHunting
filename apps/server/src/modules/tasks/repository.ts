import type { Task, TaskStatus, TaskType } from '@vanguard/contracts';
import { getDb, toJson } from '../../lib/db.ts';
import { AppError } from '../../lib/errors.ts';

interface TaskRow {
  id: string;
  user_id: string;
  parent_id: string | null;
  type: string;
  status: string;
  payload: Record<string, unknown>;
  result: Record<string, unknown> | null;
  error: string | null;
  approval: Task['approval'];
  attempts: number;
  max_attempts: number;
  created_at: Date;
  updated_at: Date;
  started_at: Date | null;
  finished_at: Date | null;
}

function toIso(value: Date | null): string | null {
  return value ? new Date(value).toISOString() : null;
}

export function mapTask(row: TaskRow): Task {
  return {
    id: row.id,
    user_id: row.user_id,
    parent_id: row.parent_id,
    type: row.type as TaskType,
    status: row.status as TaskStatus,
    payload: row.payload ?? {},
    result: row.result,
    error: row.error,
    approval: row.approval ?? null,
    attempts: row.attempts,
    max_attempts: row.max_attempts,
    created_at: new Date(row.created_at).toISOString(),
    updated_at: new Date(row.updated_at).toISOString(),
    started_at: toIso(row.started_at),
    finished_at: toIso(row.finished_at),
  };
}

export async function insertTask(input: {
  userId: string;
  type: TaskType;
  payload?: Record<string, unknown>;
  parentId?: string | null;
  maxAttempts?: number;
}): Promise<Task> {
  const sql = getDb();
  const rows = await sql<TaskRow[]>`
    insert into public.tasks (user_id, parent_id, type, payload, status, max_attempts)
    values (
      ${input.userId},
      ${input.parentId ?? null},
      ${input.type},
      ${sql.json(toJson(input.payload ?? {}))},
      'queued',
      ${input.maxAttempts ?? 3}
    )
    returning *
  `;
  const row = rows[0];
  if (!row) throw AppError.internal('Failed to create task');
  return mapTask(row);
}

export async function listTasks(userId: string, limit = 50): Promise<Task[]> {
  const sql = getDb();
  const rows = await sql<TaskRow[]>`
    select * from public.tasks
     where user_id = ${userId}
     order by created_at desc
     limit ${limit}
  `;
  return rows.map(mapTask);
}

export async function findTask(userId: string, taskId: string): Promise<Task | null> {
  const sql = getDb();
  const rows = await sql<TaskRow[]>`
    select * from public.tasks
     where id = ${taskId} and user_id = ${userId}
  `;
  const row = rows[0];
  return row ? mapTask(row) : null;
}

export async function claimNextTask(workerId: string, leaseSeconds: number): Promise<Task | null> {
  const sql = getDb();
  const rows = await sql<TaskRow[]>`
    select * from public.claim_task(${workerId}, ${leaseSeconds})
  `;
  const row = rows[0];
  return row ? mapTask(row) : null;
}

export async function heartbeatTask(
  taskId: string,
  workerId: string,
  leaseSeconds: number,
): Promise<boolean> {
  const sql = getDb();
  const rows = await sql<{ heartbeat_task: boolean }[]>`
    select public.heartbeat_task(${taskId}, ${workerId}, ${leaseSeconds}) as heartbeat_task
  `;
  return rows[0]?.heartbeat_task === true;
}

export async function finishTask(input: {
  taskId: string;
  workerId: string;
  status: TaskStatus;
  result?: Record<string, unknown>;
  error?: string;
}): Promise<boolean> {
  const sql = getDb();
  const rows = await sql<{ finish_task: boolean }[]>`
    select public.finish_task(
      ${input.taskId},
      ${input.workerId},
      ${input.status},
      ${input.result ? sql.json(toJson(input.result)) : null},
      ${input.error ?? null}
    ) as finish_task
  `;
  return rows[0]?.finish_task === true;
}

export async function resumeTask(
  taskId: string,
  userId: string,
  answer: Record<string, unknown>,
): Promise<boolean> {
  const sql = getDb();
  const rows = await sql<{ resume_task: boolean }[]>`
    select public.resume_task(${taskId}, ${userId}, ${sql.json(toJson(answer))}) as resume_task
  `;
  return rows[0]?.resume_task === true;
}

export async function approveTask(taskId: string, userId: string, note?: string): Promise<boolean> {
  const sql = getDb();
  const rows = await sql<{ approve_task: boolean }[]>`
    select public.approve_task(${taskId}, ${userId}, ${note ?? null}) as approve_task
  `;
  return rows[0]?.approve_task === true;
}

export async function cancelTask(taskId: string, userId: string): Promise<boolean> {
  const sql = getDb();
  const rows = await sql<{ cancel_task: boolean }[]>`
    select public.cancel_task(${taskId}, ${userId}) as cancel_task
  `;
  return rows[0]?.cancel_task === true;
}

export async function reclaimExpiredTasks(): Promise<number> {
  const sql = getDb();
  const rows = await sql<{ reclaim_expired_tasks: number }[]>`
    select public.reclaim_expired_tasks() as reclaim_expired_tasks
  `;
  return rows[0]?.reclaim_expired_tasks ?? 0;
}
