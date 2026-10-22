import type { ErrorHandler, NotFoundHandler } from 'hono';
import { HTTPException } from 'hono/http-exception';
import { ZodError } from 'zod';
import { AppError } from '../lib/errors.ts';
import { logger } from '../lib/logger.ts';

/**
 * Uniform error shape: { error: { code, message } }. Stack traces and internal
 * details never reach the client.
 */
export const onError: ErrorHandler = (err, c) => {
  if (err instanceof AppError) {
    return c.json({ error: { code: err.code, message: err.message } }, err.status);
  }

  if (err instanceof ZodError) {
    const message = err.issues
      .map((issue) => `${issue.path.join('.') || 'body'}: ${issue.message}`)
      .join('; ');
    return c.json({ error: { code: 'validation_error', message } }, 400);
  }

  if (err instanceof HTTPException) {
    return c.json({ error: { code: 'http_error', message: err.message } }, err.status);
  }

  logger.error('unhandled_error', {
    path: c.req.path,
    method: c.req.method,
    error: err instanceof Error ? err.message : String(err),
  });
  return c.json({ error: { code: 'internal_error', message: 'Internal server error' } }, 500);
};

export const notFound: NotFoundHandler = (c) =>
  c.json({ error: { code: 'not_found', message: 'Route not found' } }, 404);
