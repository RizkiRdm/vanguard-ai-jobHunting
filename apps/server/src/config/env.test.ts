import { describe, expect, it } from 'vitest';
import { parseEnv } from './env.ts';

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
