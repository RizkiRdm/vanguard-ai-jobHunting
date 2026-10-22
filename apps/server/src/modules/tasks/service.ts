import type { ApplyRequest, DiscoverRequest, Task } from '@vanguard/contracts';
import { AppError } from '../../lib/errors.ts';
import * as repo from './repository.ts';

export async function createDiscoveryTask(userId: string, input: DiscoverRequest): Promise<Task> {
  return repo.insertTask({
    userId,
    type: 'discover',
    payload: { query: input.query, limit: input.limit },
  });
}

export async function createApplyTask(userId: string, input: ApplyRequest): Promise<Task> {
  return repo.insertTask({
    userId,
    type: 'apply',
    payload: {
      source_url: input.source_url,
      title: input.title ?? null,
      company: input.company ?? null,
    },
  });
}

export function listUserTasks(userId: string): Promise<Task[]> {
  return repo.listTasks(userId);
}

export async function getUserTask(userId: string, taskId: string): Promise<Task> {
  const task = await repo.findTask(userId, taskId);
  if (!task) throw AppError.notFound('Task not found');
  return task;
}

/** Supplies an answer to a task that is parked waiting for a human. */
export async function answerTask(
  userId: string,
  taskId: string,
  answer: Record<string, unknown>,
): Promise<Task> {
  const resumed = await repo.resumeTask(taskId, userId, answer);
  if (!resumed) throw AppError.conflict('Task is not waiting for input');
  return getUserTask(userId, taskId);
}

/** Explicit user confirmation before a consequential external action. */
export async function approveUserTask(
  userId: string,
  taskId: string,
  note?: string,
): Promise<Task> {
  const approved = await repo.approveTask(taskId, userId, note);
  if (!approved) throw AppError.conflict('Task is not awaiting approval');
  return getUserTask(userId, taskId);
}

export async function cancelUserTask(userId: string, taskId: string): Promise<Task> {
  const cancelled = await repo.cancelTask(taskId, userId);
  if (!cancelled) throw AppError.conflict('Task cannot be cancelled in its current state');
  return getUserTask(userId, taskId);
}
