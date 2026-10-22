import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { getEnv } from '../config/env.ts';

let anon: SupabaseClient | undefined;
let admin: SupabaseClient | undefined;

/** Keyless client for public/auth operations. */
export function getAnonClient(): SupabaseClient {
  if (!anon) {
    const env = getEnv();
    anon = createClient(env.SUPABASE_URL, env.SUPABASE_ANON_KEY, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
  }
  return anon;
}

/**
 * Service-role client. Server-side only: it bypasses Row Level Security, so every
 * call site must authorise the caller first.
 */
export function getAdminClient(): SupabaseClient {
  if (!admin) {
    const env = getEnv();
    admin = createClient(env.SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
  }
  return admin;
}
