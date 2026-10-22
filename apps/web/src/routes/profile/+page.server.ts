import { fail } from '@sveltejs/kit';
import { ProfileUpdate, RESUME_MAX_BYTES, type Profile } from '@vanguard/contracts';
import { callApi, unwrap } from '../../lib/server/api';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ locals }) => {
  const result = await callApi<Profile>(locals, '/profile/me');
  if (result.ok) return { profile: result.data };
  if (result.status === 404) return { profile: null };
  unwrap(result);
  return { profile: null };
};

function readProfileUpdate(form: FormData) {
  const text = (name: string) => {
    const value = form.get(name);
    return typeof value === 'string' && value.trim() ? value.trim() : undefined;
  };
  const years = text('experience_years');
  const skills = text('skills');

  return ProfileUpdate.safeParse({
    full_name: text('full_name'),
    email: text('email'),
    phone: text('phone'),
    summary: text('summary'),
    target_role: text('target_role'),
    expected_salary: text('expected_salary'),
    location: text('location'),
    experience_years: years === undefined ? undefined : Number(years),
    skills:
      skills === undefined
        ? undefined
        : skills
            .split(',')
            .map((s) => s.trim())
            .filter(Boolean),
  });
}

export const actions: Actions = {
  save: async ({ request, locals }) => {
    const parsed = readProfileUpdate(await request.formData());
    if (!parsed.success) {
      const issue = parsed.error.issues[0];
      return fail(400, { error: `${issue?.path.join('.') || 'field'}: ${issue?.message}` });
    }

    const result = await callApi<Profile>(locals, '/profile/me', {
      method: 'PUT',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify(parsed.data),
    });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { saved: true };
  },

  uploadResume: async ({ request, locals }) => {
    const form = await request.formData();
    const file = form.get('file');
    if (!(file instanceof File) || file.size === 0) {
      return fail(400, { error: 'Choose a PDF file to upload.' });
    }
    if (file.size > RESUME_MAX_BYTES) {
      return fail(413, { error: 'Resume must be 10 MB or smaller.' });
    }

    const body = new FormData();
    body.set('file', file, file.name);

    const result = await callApi(locals, '/resumes', { method: 'POST', body });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { uploaded: true };
  },

  deleteResume: async ({ locals }) => {
    const result = await callApi(locals, '/resumes', { method: 'DELETE' });
    if (!result.ok) return fail(result.status, { error: result.message });
    return { deleted: true };
  },
};
