import { verifyAuth } from '@supabase/server/core';
import { createMiddleware } from 'hono/factory';
import type { AppEnv } from '../types.ts';
import { AppError } from '../lib/errors.ts';
import { getEnv } from '../config/env.ts';

/**
 * Verifies the caller's Supabase access token against the project JWKS.
 *
 * The user id always comes from the verified token - never from a request body,
 * query or header. A JWKS/config failure is a server problem, not a bad token.
 */
export const requireAuth = createMiddleware<AppEnv>(async (c, next) => {
  const env = getEnv();
  const { data, error } = await verifyAuth(c.req.raw, {
    auth: 'user',
    env: { url: env.SUPABASE_URL, jwks: new URL(env.SUPABASE_JWKS_URL) },
  });

  if (error) {
    if (error.status >= 500) throw AppError.internal('Token verification is misconfigured');
    throw AppError.unauthorized('Invalid or expired session');
  }

  if (!data.userClaims) throw AppError.unauthorized('Invalid or expired session');

  c.set('user', { id: data.userClaims.id, email: data.userClaims.email ?? null });
  await next();
});
