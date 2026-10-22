import { Hono } from 'hono';
import { z } from 'zod';
import { ApplyRequest, DiscoverRequest, HitlAnswer } from '@vanguard/contracts';
import { requireAuth } from '../../middleware/auth.ts';
import { rateLimit } from '../../middleware/rateLimit.ts';
import type { AppEnv } from '../../types.ts';
import { listJobsByTask } from '../jobs/repository.ts';
import * as service from './service.ts';

const uuid = z.string().uuid();
const TaskIdParams = z.object({ taskId: uuid });
const ApprovalBody = z.object({ note: z.string().max(500).optional() });

export const tasksRouter = new Hono<AppEnv>();

tasksRouter.use('*', requireAuth);

tasksRouter.get('/', async (c) => {
  const tasks = await service.listUserTasks(c.get('user').id);
  return c.json({ status: 'success', data: tasks });
});

tasksRouter.get('/:taskId', async (c) => {
  const { taskId } = TaskIdParams.parse(c.req.param());
  const task = await service.getUserTask(c.get('user').id, taskId);
  return c.json({ status: 'success', data: task });
});

tasksRouter.post('/discover', rateLimit({ scope: 'discover' }), async (c) => {
  const body = DiscoverRequest.parse(await c.req.json());
  const task = await service.createDiscoveryTask(c.get('user').id, body);
  return c.json({ status: 'success', data: task }, 201);
});

tasksRouter.post('/apply', rateLimit({ scope: 'apply' }), async (c) => {
  const body = ApplyRequest.parse(await c.req.json());
  const task = await service.createApplyTask(c.get('user').id, body);
  return c.json({ status: 'success', data: task }, 201);
});

tasksRouter.post('/:taskId/answer', async (c) => {
  const { taskId } = TaskIdParams.parse(c.req.param());
  const body = HitlAnswer.parse(await c.req.json());
  const task = await service.answerTask(c.get('user').id, taskId, { answer: body.answer });
  return c.json({ status: 'success', data: task });
});

tasksRouter.post('/:taskId/approve', async (c) => {
  const { taskId } = TaskIdParams.parse(c.req.param());
  const raw = await c.req.text();
  const body = raw ? ApprovalBody.parse(JSON.parse(raw)) : {};
  const task = await service.approveUserTask(c.get('user').id, taskId, body.note);
  return c.json({ status: 'success', data: task });
});

tasksRouter.post('/:taskId/cancel', async (c) => {
  const { taskId } = TaskIdParams.parse(c.req.param());
  const task = await service.cancelUserTask(c.get('user').id, taskId);
  return c.json({ status: 'success', data: task });
});

tasksRouter.get('/:taskId/jobs', async (c) => {
  const { taskId } = TaskIdParams.parse(c.req.param());
  const jobs = await listJobsByTask(c.get('user').id, taskId);
  return c.json({ status: 'success', data: jobs });
});
