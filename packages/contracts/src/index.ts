import { z } from 'zod';

/** Durable task lifecycle. Mirrors the `tasks.status` CHECK constraint in Postgres. */
export const TaskStatus = z.enum([
  'queued',
  'running',
  'waiting_for_user',
  'succeeded',
  'failed',
  'cancelled',
]);
export type TaskStatus = z.infer<typeof TaskStatus>;

export const TaskType = z.enum(['discover', 'apply']);
export type TaskType = z.infer<typeof TaskType>;

export const Task = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  parent_id: z.string().uuid().nullable(),
  type: TaskType,
  status: TaskStatus,
  payload: z.record(z.string(), z.unknown()),
  result: z.record(z.string(), z.unknown()).nullable(),
  error: z.string().nullable(),
  attempts: z.number().int(),
  max_attempts: z.number().int(),
  approval: z
    .object({
      reason: z.string().optional(),
      requested_at: z.string().optional(),
      approved_at: z.string().optional(),
      note: z.string().nullable().optional(),
      details: z.record(z.string(), z.unknown()).optional(),
    })
    .nullable(),
  created_at: z.string(),
  updated_at: z.string(),
  started_at: z.string().nullable(),
  finished_at: z.string().nullable(),
});
export type Task = z.infer<typeof Task>;

export const Profile = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  full_name: z.string().nullable(),
  email: z.string().nullable(),
  phone: z.string().nullable(),
  summary: z.string().nullable(),
  target_role: z.string().nullable(),
  expected_salary: z.string().nullable(),
  skills: z.array(z.string()),
  experience_years: z.number().int().nullable(),
  location: z.string().nullable(),
  resume_path: z.string().nullable(),
  resume_filename: z.string().nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});
export type Profile = z.infer<typeof Profile>;

export const ProfileUpdate = z.object({
  full_name: z.string().max(255).optional(),
  email: z.string().email().max(255).optional(),
  phone: z.string().max(50).optional(),
  summary: z.string().max(4000).optional(),
  target_role: z.string().max(255).optional(),
  expected_salary: z.string().max(100).optional(),
  skills: z.array(z.string().max(100)).max(50).optional(),
  experience_years: z.number().int().min(0).max(80).optional(),
  location: z.string().max(255).optional(),
});
export type ProfileUpdate = z.infer<typeof ProfileUpdate>;

export const Job = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  task_id: z.string().uuid().nullable(),
  source_url: z.string(),
  title: z.string(),
  company: z.string().nullable(),
  location: z.string().nullable(),
  description: z.string().nullable(),
  created_at: z.string(),
});
export type Job = z.infer<typeof Job>;

export const DiscoverRequest = z.object({
  query: z.string().min(2).max(200),
  limit: z.number().int().min(1).max(50).default(20),
});
export type DiscoverRequest = z.infer<typeof DiscoverRequest>;

export const ApplyRequest = z.object({
  source_url: z.string().url(),
  title: z.string().min(1).max(200).optional(),
  company: z.string().max(200).optional(),
});
export type ApplyRequest = z.infer<typeof ApplyRequest>;

export const HitlAnswer = z.object({
  answer: z.string().max(2000),
});
export type HitlAnswer = z.infer<typeof HitlAnswer>;

/** Resume uploads: private Supabase Storage bucket, PDF only, 10 MB cap. */
export const RESUME_MAX_BYTES = 10 * 1024 * 1024;
export const RESUME_MIME = 'application/pdf';
export const RESUME_BUCKET = 'resumes';

export const ApiError = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
  }),
});
export type ApiError = z.infer<typeof ApiError>;

export const ok = <T>(data: T) => ({ status: 'success' as const, data });
