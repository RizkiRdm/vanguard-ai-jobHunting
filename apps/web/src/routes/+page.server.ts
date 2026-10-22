import { fail } from '@sveltejs/kit';
import { ApplyRequest, DiscoverRequest, type Task } from '@vanguard/contracts';
import { callApi, unwrap } from '../lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  const tasks = unwrap(await callApi<Task[]>(locals, '/tasks'));
  return { tasks };
};

export const actions: Actions = {
  discover: async ({ request, locals }) => {
    const form = await request.formData();
    const parsed = DiscoverRequest.safeParse({
      query: form.get('query'),
      limit: Number(form.get('limit') ?? 20),
    });
    if (!parsed.success) {
      return fail(400, { error: 'Enter a job search query between 2 and 200 characters.' });
    }

    const result = await callApi<Task>(locals, '/tasks/discover', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(parsed.data),
    });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { created: result.data.id };
  },

  apply: async ({ request, locals }) => {
    const form = await request.formData();
    const parsed = ApplyRequest.safeParse({
      source_url: form.get('source_url'),
      title: form.get('title') || undefined,
      company: form.get('company') || undefined,
    });
    if (!parsed.success) {
      return fail(400, { error: 'Enter a valid job posting URL.' });
    }

    const result = await callApi<Task>(locals, '/tasks/apply', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(parsed.data),
    });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { created: result.data.id };
  },
};
