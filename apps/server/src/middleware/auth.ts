import { createMiddleware } from 'hono/factory';
import type { AppEnv } from '../types.ts';
import { AppError } from '../lib/errors.ts';
import { getAdminClient } from '../lib/supabase.ts';

/**
 * Verifies the caller's Supabase access token.
 *
 * The token is validated by Supabase Auth (signature, expiry, issuer). The user id
 * always comes from the verified token - never from a request body, query or header.
 */
export const requireAuth = createMiddleware<AppEnv>(async (c, next) => {
  const header = c.req.header('authorization') ?? '';
  const token = header.startsWith('Bearer ') ? header.slice('Bearer '.length).trim() : '';

  if (!token) {
    throw AppError.unauthorized('Missing bearer token');
  }

  const { data, error } = await getAdminClient().auth.getUser(token);
  if (error || !data.user) {
    throw AppError.unauthorized('Invalid or expired session');
  }

  c.set('user', { id: data.user.id, email: data.user.email ?? null });
  await next();
});
