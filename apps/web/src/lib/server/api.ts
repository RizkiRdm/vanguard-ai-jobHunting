import { error } from '@sveltejs/kit';
import { API_BASE_URL } from '$app/env/private';

export type ApiResult<T> = { ok: true; data: T } | { ok: false; status: number; message: string };

/**
 * Server-only call to the Hono API. The access token comes from the verified
 * cookie session, so it never reaches browser JavaScript.
 */
export async function callApi<T>(
  locals: App.Locals,
  path: string,
  init: RequestInit = {},
): Promise<ApiResult<T>> {
  if (!locals.accessToken) {
    return { ok: false, status: 401, message: 'Your session expired. Please sign in again.' };
  }

  const headers = new Headers(init.headers);
  headers.set('authorization', `Bearer ${locals.accessToken}`);

  let response: Response;
  try {
    response = await fetch(new URL(path, API_BASE_URL), { ...init, headers });
  } catch {
    return { ok: false, status: 502, message: 'The Vanguard API is unreachable.' };
  }

  const text = await response.text();
  let body: unknown;
  try {
    body = text ? JSON.parse(text) : null;
  } catch {
    body = null;
  }

  if (!response.ok) {
    const message =
      typeof body === 'object' && body !== null && 'error' in body
        ? String((body as { error: { message?: unknown } }).error.message ?? 'Request failed')
        : `Request failed (${response.status})`;
    return { ok: false, status: response.status, message };
  }

  const data =
    typeof body === 'object' && body !== null && 'data' in body
      ? (body as { data: T }).data
      : (null as T);
  return { ok: true, data };
}

/** For `load` functions: a failed API call becomes an error page, not a silent empty state. */
export function unwrap<T>(result: ApiResult<T>): T {
  if (!result.ok) throw error(result.status, result.message);
  return result.data;
}
