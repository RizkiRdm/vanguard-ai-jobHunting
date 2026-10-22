import type { Profile, ProfileUpdate } from '@vanguard/contracts';
import { eq, sql } from 'drizzle-orm';
import { userProfiles, users, type ProfileRow } from '../../db/schema.ts';
import { getDrizzle } from '../../lib/db.ts';

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
  await getDrizzle().insert(users).values({ id: userId, email }).onConflictDoNothing();
}

export async function getProfile(userId: string): Promise<Profile | null> {
  const rows = await getDrizzle()
    .select()
    .from(userProfiles)
    .where(eq(userProfiles.user_id, userId))
    .limit(1);
  const row = rows[0];
  return row ? mapProfile(row) : null;
}

export async function upsertProfile(userId: string, update: ProfileUpdate): Promise<Profile> {
  const rows = await getDrizzle()
    .insert(userProfiles)
    .values({
      user_id: userId,
      full_name: update.full_name ?? null,
      email: update.email ?? null,
      phone: update.phone ?? null,
      summary: update.summary ?? null,
      target_role: update.target_role ?? null,
      expected_salary: update.expected_salary ?? null,
      skills: update.skills ?? [],
      experience_years: update.experience_years ?? null,
      location: update.location ?? null,
    })
    .onConflictDoUpdate({
      target: userProfiles.user_id,
      set: {
        full_name: sql`excluded.full_name`,
        email: sql`excluded.email`,
        phone: sql`excluded.phone`,
        summary: sql`excluded.summary`,
        target_role: sql`excluded.target_role`,
        expected_salary: sql`excluded.expected_salary`,
        skills: sql`excluded.skills`,
        experience_years: sql`excluded.experience_years`,
        location: sql`excluded.location`,
      },
    })
    .returning();
  const row = rows[0];
  if (!row) throw new Error('Failed to upsert profile');
  return mapProfile(row);
}

export async function setResume(
  userId: string,
  resumePath: string | null,
  resumeFilename: string | null,
): Promise<void> {
  await getDrizzle()
    .insert(userProfiles)
    .values({ user_id: userId, resume_path: resumePath, resume_filename: resumeFilename })
    .onConflictDoUpdate({
      target: userProfiles.user_id,
      set: {
        resume_path: sql`excluded.resume_path`,
        resume_filename: sql`excluded.resume_filename`,
      },
    });
}
