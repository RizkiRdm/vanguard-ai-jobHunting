import { Hono } from 'hono';
import { ProfileUpdate } from '@vanguard/contracts';
import { requireAuth } from '../../middleware/auth.ts';
import { AppError } from '../../lib/errors.ts';
import type { AppEnv } from '../../types.ts';
import * as repo from './repository.ts';

export const profileRouter = new Hono<AppEnv>();

profileRouter.use('*', requireAuth);

profileRouter.get('/me', async (c) => {
  const user = c.get('user');
  await repo.ensureUserRow(user.id, user.email);
  const profile = await repo.getProfile(user.id);
  if (!profile) throw AppError.notFound('Profile not found');
  return c.json({ status: 'success', data: profile });
});

profileRouter.put('/me', async (c) => {
  const user = c.get('user');
  const body = ProfileUpdate.parse(await c.req.json());
  await repo.ensureUserRow(user.id, user.email);
  const profile = await repo.upsertProfile(user.id, body);
  return c.json({ status: 'success', data: profile });
});
