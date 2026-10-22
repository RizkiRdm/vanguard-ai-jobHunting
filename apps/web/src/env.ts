import { defineEnvVars } from '@sveltejs/kit/env';
import { z } from 'zod';

/** Validated at startup: a missing or malformed value stops the app instead of failing later. */
export const variables = defineEnvVars({
  PUBLIC_SUPABASE_URL: { public: true, schema: z.string().url() },
  PUBLIC_SUPABASE_ANON_KEY: { public: true, schema: z.string().min(1) },
  API_BASE_URL: { schema: z.string().url() },
});
