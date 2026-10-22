import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { createLogger } from './logger.ts';

let output: string[] = [];

beforeEach(() => {
  output = [];
  vi.spyOn(process.stdout, 'write').mockImplementation((chunk) => {
    output.push(String(chunk));
    return true;
  });
  vi.spyOn(process.stderr, 'write').mockImplementation((chunk) => {
    output.push(String(chunk));
    return true;
  });
});

afterEach(() => {
  vi.restoreAllMocks();
});

function lastLine(): Record<string, unknown> {
  const line = output.at(-1);
  if (!line) throw new Error('logger wrote nothing');
  return JSON.parse(line) as Record<string, unknown>;
}

describe('logger', () => {
  it('redacts credentials and sensitive content', () => {
    const log = createLogger({ service: 'test' });
    log.info('run', {
      password: 'hunter2',
      Authorization: 'Bearer abc',
      api_key: 'k',
      nested: { access_token: 't', safe: 'ok' },
    });

    const entry = lastLine();
    expect(entry.password).toBe('[redacted]');
    expect(entry.Authorization).toBe('[redacted]');
    expect(entry.api_key).toBe('[redacted]');
    expect(entry.nested).toEqual({ access_token: '[redacted]', safe: 'ok' });
    expect(JSON.stringify(entry)).not.toContain('hunter2');
  });

  it('truncates long strings', () => {
    const log = createLogger();
    log.info('cv', { summary: 'a'.repeat(600) });
    const summary = lastLine().summary as string;
    expect(summary.length).toBeLessThan(600);
    expect(summary.endsWith('[truncated]')).toBe(true);
  });

  it('drops entries below the configured level', () => {
    const log = createLogger({}, 'warn');
    log.info('ignored');
    log.warn('kept');
    expect(output).toHaveLength(1);
    expect(lastLine().msg).toBe('kept');
  });
});
