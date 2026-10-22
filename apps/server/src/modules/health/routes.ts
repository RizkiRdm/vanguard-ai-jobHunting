import { Hono } from 'hono';
import { getDb } from '../../lib/db.ts';
import { getEnv } from '../../config/env.ts';
import type { AppEnv } from '../../types.ts';

export const healthRouter = new Hono<AppEnv>();

healthRouter.get('/health', (c) =>
  c.json({ status: 'operational', service: 'vanguard-api', timestamp: new Date().toISOString() }),
);

healthRouter.get('/ready', async (c) => {
  const checks: Record<string, 'ok' | 'error'> = { database: 'error' };
  try {
    await getDb()`select 1`;
    checks.database = 'ok';
  } catch {
    checks.database = 'error';
  }

  const ready = Object.values(checks).every((v) => v === 'ok');
  return c.json(
    {
      status: ready ? 'ready' : 'not_ready',
      checks,
      environment: getEnv().NODE_ENV,
    },
    ready ? 200 : 503,
  );
});
