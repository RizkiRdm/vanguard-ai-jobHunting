/**
 * Auth UI helpers. Pure functions so sign-in/sign-up messaging is consistent
 * and testable without a browser or Supabase instance.
 */

export type SignupOutcome = { kind: 'session' } | { kind: 'confirm_email' };

export function signupOutcome(hasSession: boolean): SignupOutcome {
  return hasSession ? { kind: 'session' } : { kind: 'confirm_email' };
}

export function authErrorMessage(message: string): string {
  if (/email not confirmed/i.test(message)) {
    return 'Confirm your email before signing in. Check your inbox for the confirmation link, then try again.';
  }
  if (/invalid login credentials/i.test(message)) {
    return 'Invalid email or password.';
  }
  return message;
}

export const CONFIRM_EMAIL_INFO =
  'Account created. Check your email for a confirmation link, then sign in. If you do not see it, check spam or ask an admin to confirm the address in Supabase Auth.';
