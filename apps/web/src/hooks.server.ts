import { createServerClient } from '@supabase/ssr';
import { redirect } from '@sveltejs/kit';
import type { Handle } from '@sveltejs/kit/hooks';
import { dev } from '$app/env';
import { SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY } from '$app/env/public';

const PUBLIC_PATHS = new Set(['/login']);

export const handle: Handle = async ({ event, resolve }) => {
  event.locals.supabase = createServerClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, {
    cookies: {
      getAll: () => event.cookies.getAll(),
      setAll: (cookiesToSet) => {
        for (const { name, value, options } of cookiesToSet) {
          event.cookies.set(name, value, { ...options, path: '/', secure: !dev });
        }
      },
    },
  });

  // getUser() verifies the token with Supabase. getSession() alone is never trusted for auth.
  const {
    data: { user },
  } = await event.locals.supabase.auth.getUser();

  event.locals.user = user ? { id: user.id, email: user.email ?? null } : null;
  event.locals.accessToken = null;

  if (user) {
    const { data } = await event.locals.supabase.auth.getSession();
    event.locals.accessToken = data.session?.access_token ?? null;
  }

  if (!user && !PUBLIC_PATHS.has(event.url.pathname)) {
    redirect(303, '/login');
  }

  return resolve(event);
};
