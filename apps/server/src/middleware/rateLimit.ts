import { createMiddleware } from 'hono/factory';
import { getEnv } from '../config/env.ts';
import { AppError } from '../lib/errors.ts';
import { getDb } from '../lib/db.ts';
import type { AppEnv } from '../types.ts';

/**
 * Database-backed rate limiter. Stored in Postgres so the limit survives restarts
 * and is shared by every API and worker process.
 */
export async function consumeRateLimit(
  key: string,
  limit: number,
  windowSeconds: number,
): Promise<boolean> {
  const sql = getDb();
  const rows = await sql<{ allowed: boolean }[]>`
    select consume_rate_limit(${key}, ${limit}, ${windowSeconds}) as allowed
  `;
  return rows[0]?.allowed === true;
}

/**
 * Limits a route per authenticated user (falls back to client IP for anonymous
 * callers). Attach to expensive endpoints such as job discovery and applications.
 */
export const rateLimit = (options?: { limit?: number; windowSeconds?: number; scope?: string }) =>
  createMiddleware<AppEnv>(async (c, next) => {
    const env = getEnv();
    const user = c.get('user');
    const identity = user?.id ?? `ip:${c.req.header('x-forwarded-for') ?? 'unknown'}`;
    const key = `ratelimit:${options?.scope ?? c.req.path}:${identity}`;
    const allowed = await consumeRateLimit(
      key,
      options?.limit ?? env.RATE_LIMIT_MAX,
      options?.windowSeconds ?? env.RATE_LIMIT_WINDOW_SECONDS,
    );
    if (!allowed) {
      throw AppError.tooManyRequests('Too many requests, please slow down.');
    }
    await next();
  });
