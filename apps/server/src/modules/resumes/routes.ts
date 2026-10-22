import { Hono } from 'hono';
import { bodyLimit } from 'hono/body-limit';
import { RESUME_BUCKET, RESUME_MAX_BYTES, RESUME_MIME } from '@vanguard/contracts';
import { requireAuth } from '../../middleware/auth.ts';
import { AppError } from '../../lib/errors.ts';
import { getAdminClient } from '../../lib/supabase.ts';
import { logger } from '../../lib/logger.ts';
import type { AppEnv } from '../../types.ts';
import * as profileRepo from '../profile/repository.ts';

export const resumesRouter = new Hono<AppEnv>();

resumesRouter.use('*', requireAuth);
// formData() buffers the upload, so cap the request before it is read.
resumesRouter.post(
  '*',
  bodyLimit({
    maxSize: RESUME_MAX_BYTES + 64 * 1024,
    onError: (c) =>
      c.json({ error: { code: 'payload_too_large', message: 'Upload too large' } }, 413),
  }),
);

/** A PDF always starts with this marker; the client-supplied MIME type alone is not trusted. */
const PDF_MAGIC = '%PDF-';

resumesRouter.post('/', async (c) => {
  const user = c.get('user');

  const form = await c.req.formData().catch(() => null);
  if (!form) throw AppError.badRequest('Expected multipart/form-data body');

  const file = form.get('file');
  if (!(file instanceof File)) throw AppError.badRequest('Missing "file" field');
  if (file.size === 0) throw AppError.badRequest('Uploaded file is empty');
  if (file.size > RESUME_MAX_BYTES) {
    throw AppError.payloadTooLarge(`Resume must be smaller than ${RESUME_MAX_BYTES} bytes`);
  }
  if (file.type && file.type !== RESUME_MIME) {
    throw AppError.unsupportedMedia('Only PDF resumes are accepted');
  }

  const bytes = new Uint8Array(await file.arrayBuffer());
  const header = new TextDecoder('latin1').decode(bytes.subarray(0, 5));
  if (header !== PDF_MAGIC) {
    throw AppError.unsupportedMedia('File content is not a valid PDF');
  }

  // Object name is server generated, so a user cannot escape their own folder.
  const objectPath = `${user.id}/${crypto.randomUUID()}.pdf`;

  const admin = getAdminClient();
  const { error } = await admin.storage
    .from(RESUME_BUCKET)
    .upload(objectPath, bytes, { contentType: RESUME_MIME, upsert: true });

  if (error) {
    logger.error('resume_upload_failed', { userId: user.id, error: error.message });
    throw AppError.internal('Failed to store resume');
  }

  const previous = await profileRepo.getProfile(user.id);
  await profileRepo.ensureUserRow(user.id, user.email);
  await profileRepo.setResume(user.id, objectPath, file.name || 'resume.pdf');
  // Replace, don't accumulate: drop the file this one superseded.
  if (previous?.resume_path && previous.resume_path !== objectPath) {
    await admin.storage.from(RESUME_BUCKET).remove([previous.resume_path]);
  }

  return c.json({ status: 'success', data: { path: objectPath, filename: file.name } }, 201);
});

resumesRouter.get('/', async (c) => {
  const user = c.get('user');
  const profile = await profileRepo.getProfile(user.id);
  if (!profile?.resume_path) throw AppError.notFound('No resume uploaded');

  const { data, error } = await getAdminClient()
    .storage.from(RESUME_BUCKET)
    .createSignedUrl(profile.resume_path, 60);

  if (error || !data?.signedUrl) {
    throw AppError.internal('Failed to create signed URL');
  }

  return c.json({
    status: 'success',
    data: { url: data.signedUrl, filename: profile.resume_filename, expires_in: 60 },
  });
});

resumesRouter.delete('/', async (c) => {
  const user = c.get('user');
  const profile = await profileRepo.getProfile(user.id);
  if (!profile?.resume_path) throw AppError.notFound('No resume uploaded');

  await getAdminClient().storage.from(RESUME_BUCKET).remove([profile.resume_path]);
  await profileRepo.setResume(user.id, null, null);

  return c.json({ status: 'success', data: { deleted: true } });
});
