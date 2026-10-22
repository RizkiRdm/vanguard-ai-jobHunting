import { Hono } from 'hono';
import { requireAuth } from '../../middleware/auth.ts';
import type { AppEnv } from '../../types.ts';
import * as repo from '../jobs/repository.ts';

export const jobsRouter = new Hono<AppEnv>();

jobsRouter.use('*', requireAuth);

jobsRouter.get('/', async (c) => {
  const jobs = await repo.listJobs(c.get('user').id);
  return c.json({ status: 'success', data: jobs });
});
