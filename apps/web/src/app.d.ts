import type { SupabaseClient } from '@supabase/supabase-js';

declare global {
  namespace App {
    interface Locals {
      supabase: SupabaseClient;
      user: { id: string; email: string | null } | null;
      /** Verified access token, forwarded to the Hono API. Never sent to the browser. */
      accessToken: string | null;
    }
  }
}

export {};
