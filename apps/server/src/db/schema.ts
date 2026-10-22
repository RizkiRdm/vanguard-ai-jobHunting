import type { TaskStatus, TaskType } from '@vanguard/contracts';
import {
  bigint,
  date,
  index,
  integer,
  jsonb,
  pgTable,
  text,
  timestamp,
  uuid,
} from 'drizzle-orm/pg-core';

/**
 * Typed mirror of `supabase/migrations/*.sql`. The SQL files stay authoritative:
 * RLS policies, triggers and the queue functions cannot be expressed here.
 * Column names and property names are identical, so rows map without translation.
 */

const createdAt = timestamp('created_at', { withTimezone: true, mode: 'date' })
  .notNull()
  .defaultNow();
const updatedAt = timestamp('updated_at', { withTimezone: true, mode: 'date' })
  .notNull()
  .defaultNow();

export const users = pgTable('users', {
  id: uuid('id').primaryKey(),
  email: text('email'),
  version: integer('version').notNull().default(1),
  created_at: createdAt,
  updated_at: updatedAt,
});

export const userProfiles = pgTable('user_profiles', {
  id: uuid('id').primaryKey().defaultRandom(),
  user_id: uuid('user_id').notNull().unique(),
  full_name: text('full_name'),
  email: text('email'),
  phone: text('phone'),
  summary: text('summary'),
  target_role: text('target_role'),
  expected_salary: text('expected_salary'),
  skills: text('skills').array().notNull().default([]),
  experience_years: integer('experience_years'),
  location: text('location'),
  resume_path: text('resume_path'),
  resume_filename: text('resume_filename'),
  created_at: createdAt,
  updated_at: updatedAt,
});

export const tasks = pgTable(
  'tasks',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    user_id: uuid('user_id').notNull(),
    parent_id: uuid('parent_id'),
    type: text('type').$type<TaskType>().notNull(),
    status: text('status').$type<TaskStatus>().notNull().default('queued'),
    payload: jsonb('payload').$type<Record<string, unknown>>().notNull().default({}),
    result: jsonb('result').$type<Record<string, unknown>>(),
    error: text('error'),
    approval: jsonb('approval').$type<{
      reason?: string;
      requested_at?: string;
      approved_at?: string;
      note?: string | null;
      details?: Record<string, unknown>;
    }>(),
    attempts: integer('attempts').notNull().default(0),
    max_attempts: integer('max_attempts').notNull().default(3),
    worker_id: text('worker_id'),
    lease_expires_at: timestamp('lease_expires_at', { withTimezone: true, mode: 'date' }),
    heartbeat_at: timestamp('heartbeat_at', { withTimezone: true, mode: 'date' }),
    next_run_at: timestamp('next_run_at', { withTimezone: true, mode: 'date' })
      .notNull()
      .defaultNow(),
    started_at: timestamp('started_at', { withTimezone: true, mode: 'date' }),
    finished_at: timestamp('finished_at', { withTimezone: true, mode: 'date' }),
    created_at: createdAt,
    updated_at: updatedAt,
  },
  (table) => [
    index('tasks_claimable_idx').on(table.status, table.next_run_at, table.created_at),
    index('tasks_user_idx').on(table.user_id, table.created_at),
    index('tasks_parent_idx').on(table.parent_id),
  ],
);

export const jobs = pgTable(
  'jobs',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    user_id: uuid('user_id').notNull(),
    task_id: uuid('task_id'),
    source_url: text('source_url').notNull(),
    title: text('title').notNull(),
    company: text('company'),
    location: text('location'),
    description: text('description'),
    created_at: createdAt,
  },
  (table) => [index('jobs_user_idx').on(table.user_id, table.created_at)],
);

export const documents = pgTable(
  'documents',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    user_id: uuid('user_id').notNull(),
    task_id: uuid('task_id'),
    doc_type: text('doc_type').notNull(),
    content: text('content').notNull(),
    token_cost: integer('token_cost').notNull().default(0),
    created_at: createdAt,
  },
  (table) => [index('documents_user_idx').on(table.user_id, table.created_at)],
);

export const llmUsageLog = pgTable(
  'llm_usage_log',
  {
    id: uuid('id').primaryKey().defaultRandom(),
    user_id: uuid('user_id'),
    model: text('model').notNull(),
    prompt_tokens: integer('prompt_tokens').notNull().default(0),
    completion_tokens: integer('completion_tokens').notNull().default(0),
    total_tokens: integer('total_tokens').notNull().default(0),
    created_at: createdAt,
  },
  (table) => [index('llm_usage_user_idx').on(table.user_id, table.created_at)],
);

export const budgetCounters = pgTable('budget_counters', {
  user_id: uuid('user_id').primaryKey(),
  used_tokens: bigint('used_tokens', { mode: 'number' }).notNull().default(0),
  budget_day: date('budget_day').notNull().defaultNow(),
  updated_at: updatedAt,
});

export const rateLimits = pgTable('rate_limits', {
  key: text('key').primaryKey(),
  window_start: timestamp('window_start', { withTimezone: true, mode: 'date' })
    .notNull()
    .defaultNow(),
  count: integer('count').notNull().default(0),
});

export type TaskRow = typeof tasks.$inferSelect;
export type JobRow = typeof jobs.$inferSelect;
export type ProfileRow = typeof userProfiles.$inferSelect;
