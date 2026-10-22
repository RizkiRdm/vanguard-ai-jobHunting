import type { Task, TaskStatus, TaskType } from '@vanguard/contracts';
import { and, desc, eq, sql, type SQL } from 'drizzle-orm';
import type { TaskRow } from '../../db/schema.ts';
import { tasks } from '../../db/schema.ts';
import { getDrizzle } from '../../lib/db.ts';
import { AppError } from '../../lib/errors.ts';

function toIso(value: Date | null): string | null {
  return value ? new Date(value).toISOString() : null;
}

export function mapTask(row: TaskRow): Task {
  return {
    id: row.id,
    user_id: row.user_id,
    parent_id: row.parent_id,
    type: row.type,
    status: row.status,
    payload: row.payload ?? {},
    result: row.result ?? null,
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

/** Drizzle cannot infer the shape of a set-returning SQL function. */
async function selectRows<T>(query: SQL): Promise<T[]> {
  return (await getDrizzle().execute(query)) as unknown as T[];
}

export async function insertTask(input: {
  userId: string;
  type: TaskType;
  payload?: Record<string, unknown>;
  parentId?: string | null;
  maxAttempts?: number;
}): Promise<Task> {
  const rows = await getDrizzle()
    .insert(tasks)
    .values({
      user_id: input.userId,
      parent_id: input.parentId ?? null,
      type: input.type,
      payload: input.payload ?? {},
      status: 'queued',
      max_attempts: input.maxAttempts ?? 3,
    })
    .returning();
  const row = rows[0];
  if (!row) throw AppError.internal('Failed to create task');
  return mapTask(row);
}

export async function listTasks(userId: string, limit = 50): Promise<Task[]> {
  const rows = await getDrizzle()
    .select()
    .from(tasks)
    .where(eq(tasks.user_id, userId))
    .orderBy(desc(tasks.created_at))
    .limit(limit);
  return rows.map(mapTask);
}

export async function findTask(userId: string, taskId: string): Promise<Task | null> {
  const rows = await getDrizzle()
    .select()
    .from(tasks)
    .where(and(eq(tasks.id, taskId), eq(tasks.user_id, userId)))
    .limit(1);
  const row = rows[0];
  return row ? mapTask(row) : null;
}

export async function claimNextTask(workerId: string, leaseSeconds: number): Promise<Task | null> {
  const rows = await selectRows<TaskRow>(
    sql`select * from public.claim_task(${workerId}, ${leaseSeconds})`,
  );
  const row = rows[0];
  return row ? mapTask(row) : null;
}

export async function heartbeatTask(
  taskId: string,
  workerId: string,
  leaseSeconds: number,
): Promise<boolean> {
  const rows = await selectRows<{ heartbeat_task: boolean }>(
    sql`select public.heartbeat_task(${taskId}, ${workerId}, ${leaseSeconds}) as heartbeat_task`,
  );
  return rows[0]?.heartbeat_task === true;
}

export async function finishTask(input: {
  taskId: string;
  workerId: string;
  status: TaskStatus;
  result?: Record<string, unknown>;
  error?: string;
}): Promise<boolean> {
  const result = input.result ? JSON.stringify(input.result) : null;
  const rows = await selectRows<{ finish_task: boolean }>(
    sql`select public.finish_task(
          ${input.taskId}, ${input.workerId}, ${input.status},
          ${result}::jsonb, ${input.error ?? null}
        ) as finish_task`,
  );
  return rows[0]?.finish_task === true;
}

export async function resumeTask(
  taskId: string,
  userId: string,
  answer: Record<string, unknown>,
): Promise<boolean> {
  const rows = await selectRows<{ resume_task: boolean }>(
    sql`select public.resume_task(${taskId}, ${userId}, ${JSON.stringify(answer)}::jsonb) as resume_task`,
  );
  return rows[0]?.resume_task === true;
}

export async function approveTask(taskId: string, userId: string, note?: string): Promise<boolean> {
  const rows = await selectRows<{ approve_task: boolean }>(
    sql`select public.approve_task(${taskId}, ${userId}, ${note ?? null}) as approve_task`,
  );
  return rows[0]?.approve_task === true;
}

export async function cancelTask(taskId: string, userId: string): Promise<boolean> {
  const rows = await selectRows<{ cancel_task: boolean }>(
    sql`select public.cancel_task(${taskId}, ${userId}) as cancel_task`,
  );
  return rows[0]?.cancel_task === true;
}

export async function reclaimExpiredTasks(): Promise<number> {
  const rows = await selectRows<{ reclaim_expired_tasks: number }>(
    sql`select public.reclaim_expired_tasks() as reclaim_expired_tasks`,
  );
  return rows[0]?.reclaim_expired_tasks ?? 0;
}
