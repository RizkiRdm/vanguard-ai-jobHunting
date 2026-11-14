import { describe, expect, it } from 'vitest';
import { authErrorMessage, CONFIRM_EMAIL_INFO, signupOutcome } from './auth';

describe('auth helpers', () => {
  it('treats signup with a session as signed in', () => {
    expect(signupOutcome(true)).toEqual({ kind: 'session' });
  });

  it('treats signup without a session as confirmation required', () => {
    expect(signupOutcome(false)).toEqual({ kind: 'confirm_email' });
    expect(CONFIRM_EMAIL_INFO).toMatch(/confirmation link/i);
  });

  it('maps unconfirmed-email sign-in to actionable guidance', () => {
    expect(authErrorMessage('Email not confirmed')).toMatch(/Confirm your email/);
  });

  it('maps invalid credentials without leaking details', () => {
    expect(authErrorMessage('Invalid login credentials')).toBe('Invalid email or password.');
  });

  it('preserves other errors', () => {
    expect(authErrorMessage('User already registered')).toBe('User already registered');
  });
});
