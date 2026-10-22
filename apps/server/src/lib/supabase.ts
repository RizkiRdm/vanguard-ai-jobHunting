import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import { getEnv } from '../config/env.ts';

let admin: SupabaseClient | undefined;

/**
 * Secret-key client. Server-side only: it bypasses Row Level Security, so every
 * call site must authorise the caller first.
 */
export function getAdminClient(): SupabaseClient {
  if (!admin) {
    const env = getEnv();
    admin = createClient(env.SUPABASE_URL, env.SUPABASE_SECRET_KEY, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
  }
  return admin;
}
