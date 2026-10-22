import { serve } from '@hono/node-server';
import { createApp } from './app.ts';
import { getEnv } from './config/env.ts';
import { logger } from './lib/logger.ts';
import { closeDb } from './lib/db.ts';

const env = getEnv();
const app = createApp();

const server = serve({ fetch: app.fetch, port: env.API_PORT }, (info) => {
  logger.info('api_started', { port: info.port, environment: env.NODE_ENV });
});

async function shutdown(signal: string): Promise<void> {
  logger.info('shutdown_signal_received', { signal });
  await server.close();
  await closeDb();
  process.exit(0);
}

process.on('SIGINT', () => void shutdown('SIGINT'));
process.on('SIGTERM', () => void shutdown('SIGTERM'));
