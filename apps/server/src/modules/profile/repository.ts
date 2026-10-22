import type { Profile, ProfileUpdate } from '@vanguard/contracts';
import { getDb } from '../../lib/db.ts';

interface ProfileRow {
  id: string;
  user_id: string;
  full_name: string | null;
  email: string | null;
  phone: string | null;
  summary: string | null;
  target_role: string | null;
  expected_salary: string | null;
  skills: string[];
  experience_years: number | null;
  location: string | null;
  resume_path: string | null;
  resume_filename: string | null;
  created_at: Date;
  updated_at: Date;
}

function mapProfile(row: ProfileRow): Profile {
  return {
    id: row.id,
    user_id: row.user_id,
    full_name: row.full_name,
    email: row.email,
    phone: row.phone,
    summary: row.summary,
    target_role: row.target_role,
    expected_salary: row.expected_salary,
    skills: row.skills ?? [],
    experience_years: row.experience_years,
    location: row.location,
    resume_path: row.resume_path,
    resume_filename: row.resume_filename,
    created_at: new Date(row.created_at).toISOString(),
    updated_at: new Date(row.updated_at).toISOString(),
  };
}

/**
 * Guarantees a public.users row exists for the authenticated user.
 * The auth trigger normally creates it; this covers users that predate the trigger.
 */
export async function ensureUserRow(userId: string, email: string | null): Promise<void> {
  const sql = getDb();
  await sql`
    insert into public.users (id, email)
    values (${userId}, ${email})
    on conflict (id) do nothing
  `;
}

export async function getProfile(userId: string): Promise<Profile | null> {
  const sql = getDb();
  const rows = await sql<ProfileRow[]>`
    select * from public.user_profiles where user_id = ${userId}
  `;
  const row = rows[0];
  return row ? mapProfile(row) : null;
}

export async function upsertProfile(userId: string, update: ProfileUpdate): Promise<Profile> {
  const sql = getDb();
  const rows = await sql<ProfileRow[]>`
    insert into public.user_profiles (user_id, full_name, email, phone, summary,
                                      target_role, expected_salary, skills,
                                      experience_years, location)
    values (
      ${userId},
      ${update.full_name ?? null},
      ${update.email ?? null},
      ${update.phone ?? null},
      ${update.summary ?? null},
      ${update.target_role ?? null},
      ${update.expected_salary ?? null},
      ${update.skills ?? sql.array([])},
      ${update.experience_years ?? null},
      ${update.location ?? null}
    )
    on conflict (user_id) do update set
      full_name = excluded.full_name,
      email = excluded.email,
      phone = excluded.phone,
      summary = excluded.summary,
      target_role = excluded.target_role,
      expected_salary = excluded.expected_salary,
      skills = excluded.skills,
      experience_years = excluded.experience_years,
      location = excluded.location
    returning *
  `;
  const row = rows[0];
  if (!row) throw new Error('Failed to upsert profile');
  return mapProfile(row);
}

export async function setResume(
  userId: string,
  resumePath: string | null,
  resumeFilename: string | null,
): Promise<void> {
  const sql = getDb();
  await sql`
    insert into public.user_profiles (user_id, resume_path, resume_filename)
    values (${userId}, ${resumePath}, ${resumeFilename})
    on conflict (user_id) do update
      set resume_path = excluded.resume_path,
          resume_filename = excluded.resume_filename
  `;
}
