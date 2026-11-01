import { describe, expect, it } from 'vitest';
import { envStatus, isAtLeast, minNodeVersion, parseEnvFile } from './doctor.mjs';

describe('parseEnvFile', () => {
  it('reads keys, skipping comments and blanks', () => {
    const parsed = parseEnvFile('# note\nA=1\n\nexport B="two"\nC=\'three\'\nD=\n');
    expect(parsed).toEqual({ A: '1', B: 'two', C: 'three', D: '' });
  });
});

describe('envStatus', () => {
  it('separates present, placeholder and missing without exposing values', () => {
    const status = envStatus(['A', 'B', 'C'], { A: 'real', B: 'REPLACE_ME', C: '' });
    expect(status).toEqual([
      { name: 'A', status: 'present' },
      { name: 'B', status: 'placeholder' },
      { name: 'C', status: 'missing' },
    ]);
  });
});

describe('node version', () => {
  it('parses the major from engines', () => {
    expect(minNodeVersion('>=22')).toBe(22);
    expect(minNodeVersion(undefined)).toBe(0);
  });

  it('compares against the minimum', () => {
    expect(isAtLeast('24.18.0', 22)).toBe(true);
    expect(isAtLeast('22.0.0', 22)).toBe(true);
    expect(isAtLeast('20.11.1', 22)).toBe(false);
  });
});
