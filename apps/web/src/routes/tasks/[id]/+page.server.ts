import { fail } from '@sveltejs/kit';
import { HitlAnswer, type Job, type Task } from '@vanguard/contracts';
import { callApi, unwrap } from '../../../lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals, params }) => {
  const task = unwrap(await callApi<Task>(locals, `/tasks/${params.id}`));
  const jobsResult = await callApi<Job[]>(locals, `/tasks/${params.id}/jobs`);
  return { task, jobs: jobsResult.ok ? jobsResult.data : [] };
};

export const actions: Actions = {
  cancel: async ({ locals, params }) => {
    const result = await callApi<Task>(locals, `/tasks/${params.id}/cancel`, { method: 'POST' });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { cancelled: true };
  },

  approve: async ({ locals, params, request }) => {
    const form = await request.formData();
    const note = form.get('note');
    const result = await callApi<Task>(locals, `/tasks/${params.id}/approve`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ note: typeof note === 'string' ? note : undefined }),
    });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { approved: true };
  },

  answer: async ({ locals, params, request }) => {
    const form = await request.formData();
    const parsed = HitlAnswer.safeParse({ answer: form.get('answer') });
    if (!parsed.success) return fail(400, { error: 'Enter an answer before submitting.' });

    const result = await callApi<Task>(locals, `/tasks/${params.id}/answer`, {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(parsed.data),
    });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { answered: true };
  },
};
