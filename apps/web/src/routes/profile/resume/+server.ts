import { error, redirect } from '@sveltejs/kit';
import { callApi } from '../../../lib/server/api';
import type { RequestHandler } from './$types';

/** Short-lived signed URL, minted server-side; the bucket stays private. */
export const GET: RequestHandler = async ({ locals }) => {
  const result = await callApi<{ url: string }>(locals, '/resumes');
  if (!result.ok) throw error(result.status, result.message);
  redirect(303, result.data.url);
};
