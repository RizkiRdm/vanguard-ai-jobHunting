import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { getEnv } from './config/env.ts';
import { onError, notFound } from './middleware/error.ts';
import { healthRouter } from './modules/health/routes.ts';
import { jobsRouter } from './modules/jobs/routes.ts';
import { profileRouter } from './modules/profile/routes.ts';
import { resumesRouter } from './modules/resumes/routes.ts';
import { tasksRouter } from './modules/tasks/routes.ts';
import type { AppEnv } from './types.ts';

export function createApp(): Hono<AppEnv> {
  const env = getEnv();
  const app = new Hono<AppEnv>();

  app.onError(onError);

  // Narrow CORS: only the configured web origin, with credentials.
  app.use(
    '*',
    cors({
      origin: [env.WEB_ORIGIN],
      allowMethods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
      allowHeaders: ['Authorization', 'Content-Type'],
      credentials: true,
      maxAge: 600,
    }),
  );

  app.route('/', healthRouter);
  app.route('/jobs', jobsRouter);
  app.route('/profile', profileRouter);
  app.route('/resumes', resumesRouter);
  app.route('/tasks', tasksRouter);

  app.notFound(notFound);

  return app;
}
