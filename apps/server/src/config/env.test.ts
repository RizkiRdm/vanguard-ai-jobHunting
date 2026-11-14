import type { PathLike } from 'node:fs';
import { resolve } from 'node:path';
import { describe, expect, it, vi } from 'vitest';
import { getEnv, parseEnv, REPO_ROOT_ENV, setEnv } from './env.ts';

const REQUIRED = {
  DATABASE_URL: 'postgres://u:p@localhost:5432/db',
  SUPABASE_URL: 'https://example.supabase.co',
  SUPABASE_PUBLISHABLE_KEY: 'anon',
  SUPABASE_SECRET_KEY: 'service',
  SUPABASE_JWKS_URL: 'https://example.supabase.co/auth/v1/.well-known/jwks.json',
  GEMINI_API_KEY: 'key',
};

describe('parseEnv', () => {
  it('applies safe defaults', () => {
    const env = parseEnv({ ...REQUIRED });
    expect(env.NODE_ENV).toBe('development');
    expect(env.API_PORT).toBe(8000);
    expect(env.WORKER_CONCURRENCY).toBe(2);
    expect(env.BROWSER_HEADLESS).toBe(true);
  });

  it('fails fast when required values are missing', () => {
    expect(() => parseEnv({})).toThrow(/DATABASE_URL/);
    expect(() => parseEnv({})).toThrow(/SUPABASE_SECRET_KEY/);
  });

  it('rejects malformed values instead of falling back', () => {
    expect(() => parseEnv({ ...REQUIRED, SUPABASE_URL: 'not-a-url' })).toThrow(
      /SUPABASE_URL must be a URL/,
    );
    expect(() => parseEnv({ ...REQUIRED, API_PORT: '70000' })).toThrow(/API_PORT/);
  });

  it('reads BROWSER_HEADLESS=false as false', () => {
    expect(parseEnv({ ...REQUIRED, BROWSER_HEADLESS: 'false' }).BROWSER_HEADLESS).toBe(false);
  });
});

describe('getEnv', () => {
  it('loads .env from the working directory and the repo root', () => {
    setEnv(parseEnv({ ...REQUIRED }));
    const calls: Array<string | undefined> = [];
    const spy = vi.spyOn(process, 'loadEnvFile').mockImplementation((path?: PathLike) => {
      calls.push(typeof path === 'string' ? path : undefined);
    });
    getEnv();
    spy.mockRestore();
    expect(calls).toContain(resolve(process.cwd(), '.env'));
    expect(calls).toContain(REPO_ROOT_ENV);
  });
});
