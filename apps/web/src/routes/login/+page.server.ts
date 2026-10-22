import { redirect } from '@sveltejs/kit';
import { SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY } from '$app/env/public';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  if (locals.user) redirect(303, '/');

  return {
    supabaseUrl: SUPABASE_URL,
    supabaseKey: SUPABASE_PUBLISHABLE_KEY,
  };
};
