import { z } from 'zod';

const EnvSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  LOG_LEVEL: z.enum(['debug', 'info', 'warn', 'error']).default('info'),

  // PostgreSQL (Supabase) - direct connection for the task queue and app data.
  DATABASE_URL: z.string().min(1, 'DATABASE_URL is required'),

  // Supabase Auth + Storage
  SUPABASE_URL: z.string().url('SUPABASE_URL must be a URL'),
  SUPABASE_ANON_KEY: z.string().min(1, 'SUPABASE_ANON_KEY is required'),
  SUPABASE_SERVICE_ROLE_KEY: z.string().min(1, 'SUPABASE_SERVICE_ROLE_KEY is required'),

  // AI provider
  GEMINI_API_KEY: z.string().min(1, 'GEMINI_API_KEY is required'),
  AI_MODEL: z.string().default('gemini-2.0-flash'),
  DAILY_TOKEN_BUDGET: z.coerce.number().int().positive().default(1_000_000),

  // HTTP
  API_PORT: z.coerce.number().int().min(1).max(65535).default(8000),
  API_BASE_URL: z.string().default('http://localhost:8000'),
  WEB_ORIGIN: z.string().default('http://localhost:5173'),
  RATE_LIMIT_MAX: z.coerce.number().int().min(1).default(30),
  RATE_LIMIT_WINDOW_SECONDS: z.coerce.number().int().min(1).default(60),

  // Worker
  WORKER_CONCURRENCY: z.coerce.number().int().min(1).max(8).default(2),
  WORKER_POLL_MS: z.coerce.number().int().min(100).default(2000),
  TASK_LEASE_SECONDS: z.coerce.number().int().min(30).default(180),
  TASK_MAX_ATTEMPTS: z.coerce.number().int().min(1).max(10).default(3),

  // Browser
  BROWSER_HEADLESS: z
    .string()
    .default('true')
    .transform((v) => v !== 'false'),
  BROWSER_TIMEOUT_MS: z.coerce.number().int().min(1000).default(30_000),
});

export type Env = z.infer<typeof EnvSchema>;

let cached: Env | undefined;

/** Validates process.env. Throws on missing or malformed values so startup fails fast. */
export function parseEnv(source: NodeJS.ProcessEnv = process.env): Env {
  const parsed = EnvSchema.safeParse(source);
  if (!parsed.success) {
    const detail = parsed.error.issues
      .map((issue) => `${issue.path.join('.') || 'env'}: ${issue.message}`)
      .join('; ');
    throw new Error(`Invalid environment configuration: ${detail}`);
  }
  return parsed.data;
}

export function getEnv(): Env {
  cached ??= parseEnv();
  return cached;
}

/** Test helper: override the memoized environment. */
export function setEnv(env: Env): void {
  cached = env;
}
