import { getEnv } from './config/env.ts';
import { logger } from './lib/logger.ts';
import { closeDb } from './lib/db.ts';
import { TaskWorker } from './modules/tasks/worker.ts';

const env = getEnv();
const worker = new TaskWorker();

const shutdown = (signal: string) => {
  logger.info('shutdown_signal_received', { signal });
  worker.stop();
};

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

logger.info('worker_boot', { environment: env.NODE_ENV });

worker
  .run()
  .catch((error: unknown) => {
    logger.error('worker_crashed', {
      error: error instanceof Error ? error.message : String(error),
    });
    process.exitCode = 1;
  })
  .finally(() => closeDb());
