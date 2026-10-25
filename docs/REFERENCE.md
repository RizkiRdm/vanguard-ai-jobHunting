# Reference

Exact values, names and shapes. If this file and the code disagree, the code wins;
fix the file.

## npm scripts

| Script                 | Runs                                                    | Notes                                                            |
| ---------------------- | ------------------------------------------------------- | ---------------------------------------------------------------- |
| `npm run dev`          | every workspace's `dev`                                 | API + web together; no worker                                    |
| `npm run dev:server`   | `tsx watch src/api.ts` (`@vanguard/server`)             | API on `API_PORT`                                                |
| `npm run dev:web`      | `vite dev --port 5173` (`@vanguard/web`)                | needs `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`, `API_BASE_URL` |
| `npm run worker`       | `tsx src/worker.ts`                                     | long-running; claims tasks                                       |
| `npm run build`        | `vite build` (`@vanguard/web`)                          | adapter-node output in `apps/web/build`                          |
| `npm test`             | `vitest run`                                            | DB suite skips without `TEST_DATABASE_URL`                       |
| `npm run test:watch`   | `vitest`                                                |                                                                  |
| `npm run typecheck`    | `tsc -p apps/server` + `npm run check -w @vanguard/web` | `svelte-check`                                                   |
| `npm run lint`         | `eslint .`                                              | flat config, `no-explicit-any` is an error                       |
| `npm run format`       | `prettier --write .`                                    |                                                                  |
| `npm run format:check` | `prettier --check .`                                    |                                                                  |
| `npm run db:migrate`   | `tsx apps/server/src/scripts/migrate.ts`                | applies `supabase/migrations/*.sql`, records each name           |

## Environment variables

Server (`apps/server/src/config/env.ts`). Missing or malformed values abort startup
with the field names listed. No value has a fallback secret.

| Variable                    | Required | Default                 | Used for                                  |
| --------------------------- | -------- | ----------------------- | ----------------------------------------- |
| `NODE_ENV`                  | no       | `development`           | `development` \| `test` \| `production`   |
| `LOG_LEVEL`                 | no       | `info`                  | `debug` \| `info` \| `warn` \| `error`    |
| `DATABASE_URL`              | yes      | —                       | Postgres. Use the Supavisor pooler        |
| `SUPABASE_URL`              | yes      | —                       | JWKS derivation, Storage client           |
| `SUPABASE_PUBLISHABLE_KEY`  | yes      | —                       | Web sign-in (read by `apps/web` too)      |
| `SUPABASE_SECRET_KEY`       | yes      | —                       | Storage, server only, bypasses RLS        |
| `SUPABASE_JWKS_URL`         | yes      | —                       | Local access-token verification           |
| `GEMINI_API_KEY`            | yes      | —                       | Google AI Studio key                      |
| `AI_MODEL`                  | no       | `gemini-2.0-flash`      | Model id                                  |
| `DAILY_TOKEN_BUDGET`        | no       | `1000000`               | Per-user daily token cap                  |
| `API_PORT`                  | no       | `8000`                  | API listen port                           |
| `API_BASE_URL`              | no       | `http://localhost:8000` | Where the web app sends API calls         |
| `WEB_ORIGIN`                | no       | `http://localhost:5173` | The only allowed CORS origin              |
| `RATE_LIMIT_MAX`            | no       | `30`                    | Requests per window per user and scope    |
| `RATE_LIMIT_WINDOW_SECONDS` | no       | `60`                    | Fixed window length                       |
| `WORKER_CONCURRENCY`        | no       | `2`                     | Tasks running at once, 1–8                |
| `WORKER_POLL_MS`            | no       | `2000`                  | Idle poll interval, min 100               |
| `TASK_LEASE_SECONDS`        | no       | `180`                   | Claim lease, min 30; heartbeat at a third |
| `TASK_MAX_ATTEMPTS`         | no       | `3`                     | Attempts before a task fails, 1–10        |
| `BROWSER_HEADLESS`          | no       | `true`                  | `false` shows the window                  |
| `BROWSER_TIMEOUT_MS`        | no       | `30000`                 | Navigation and action timeout, min 1000   |

Web (`apps/web/src/env.ts`, also read at build time): `SUPABASE_URL` (public),
`SUPABASE_PUBLISHABLE_KEY` (public), `API_BASE_URL` (server-side only).

Test only: `TEST_DATABASE_URL`. When set, the repository integration suite runs
against that database and applies the migrations itself.

## HTTP API

Base URL is `API_BASE_URL`. Every route except `/health` and `/ready` requires
`Authorization: Bearer <supabase access token>`; the token is verified against
`SUPABASE_JWKS_URL`, and the user id comes from the verified claims only.

Success responses are `{ "status": "success", "data": … }`. Failures are
`{ "error": { "code": "…", "message": "…" } }` with a matching status code. No
stack traces.

| Method | Path                     | Auth | Body / query                          | Success                           | Notes                                                            |
| ------ | ------------------------ | ---- | ------------------------------------- | --------------------------------- | ---------------------------------------------------------------- |
| GET    | `/health`                | no   | —                                     | 200                               | Static liveness                                                  |
| GET    | `/ready`                 | no   | —                                     | 200 / 503                         | Runs `select 1`; 503 `not_ready` when the database is down       |
| GET    | `/jobs`                  | yes  | —                                     | 200                               | All jobs for the caller, newest first                            |
| GET    | `/profile/me`            | yes  | —                                     | 200 / 404                         | 404 until the profile exists                                     |
| PUT    | `/profile/me`            | yes  | `ProfileUpdate` (all fields optional) | 200                               | Upsert; a field left out is cleared                              |
| POST   | `/resumes`               | yes  | `multipart/form-data`, field `file`   | 201 `{path, filename}`            | PDF only, ≤ 10 MB, `%PDF-` checked; replaces the previous object |
| GET    | `/resumes`               | yes  | —                                     | 200 `{url, filename, expires_in}` | New 60 s signed URL; 404 if none                                 |
| DELETE | `/resumes`               | yes  | —                                     | 200 `{deleted:true}`              | Removes object and profile pointers                              |
| GET    | `/tasks`                 | yes  | —                                     | 200 `Task[]`                      | Caller's tasks, newest first                                     |
| GET    | `/tasks/:taskId`         | yes  | —                                     | 200 `Task` / 404                  | Other users' tasks are 404, not 403                              |
| POST   | `/tasks/discover`        | yes  | `{query, limit?}`                     | 201 `Task`                        | Rate limited, scope `discover`; 429 `rate_limited`               |
| POST   | `/tasks/apply`           | yes  | `{source_url, title?, company?}`      | 201 `Task`                        | Rate limited, scope `apply`                                      |
| POST   | `/tasks/:taskId/answer`  | yes  | `{answer}`                            | 200 `Task`                        | Only while `waiting_for_user`, otherwise 409                     |
| POST   | `/tasks/:taskId/approve` | yes  | `{note?}` (optional body)             | 200 `Task`                        | Records approval and re-queues; only path that enables submit    |
| POST   | `/tasks/:taskId/cancel`  | yes  | —                                     | 200 `Task`                        | From any non-final state                                         |
| GET    | `/tasks/:taskId/jobs`    | yes  | —                                     | 200 `Job[]`                       | Listings created by that task                                    |

Validation errors are 400 `validation_error` with the failing paths. Upload limits
return 413 `payload_too_large`; a wrong file type returns 415
`unsupported_media_type`. An invalid or expired token returns 401
`unauthenticated`.

Common `Task` fields: `id`, `user_id`, `parent_id`, `type` (`discover` | `apply`),
`status`, `payload`, `result`, `error`, `attempts`, `max_attempts`, `approval` (a
pending request with `reason`/`details`, or an approval with
`approved_at`/`note`, both carrying `details`), `created_at`, `updated_at`,
`started_at`, `finished_at`.

## Task states

| State              | Meaning                                                      |
| ------------------ | ------------------------------------------------------------ |
| `queued`           | waiting for a worker claim (also the retry state)            |
| `running`          | a worker holds a lease                                       |
| `waiting_for_user` | parked: needs an approval or an answer                       |
| `succeeded`        | finished; `result` holds the outcome                         |
| `failed`           | attempts exhausted or unrecoverable; `error` holds a summary |
| `cancelled`        | cancelled by the owner                                       |

Transitions only happen through the SQL functions below, never a bare `UPDATE`.
Lease expiry requeues a `running` task through `reclaim_expired_tasks`.

## SQL functions

Defined in `supabase/migrations`. Queue, budget and rate-limit functions are
`SECURITY DEFINER` with `search_path = ''`, executable by `service_role` only;
`public`, `anon` and `authenticated` are revoked.

| Function                | Signature                                                                             | Effect                                                                                                |
| ----------------------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| `claim_task`            | `(p_worker text, p_lease_seconds integer) → setof tasks`                              | Claims the oldest claimable task with `FOR UPDATE SKIP LOCKED`, sets `running`, lease, `attempts + 1` |
| `heartbeat_task`        | `(p_task uuid, p_worker text, p_lease_seconds integer) → boolean`                     | Extends the lease; false if the caller no longer owns it                                              |
| `finish_task`           | `(p_task uuid, p_worker text, p_status text, p_result jsonb, p_error text) → boolean` | Terminal transition, guarded by worker id and `running`                                               |
| `reclaim_expired_tasks` | `() → integer`                                                                        | Expired leases: requeue with backoff, or fail when attempts are exhausted                             |
| `retry_task`            | `(p_task uuid, p_worker text, p_error text, p_backoff_seconds integer) → boolean`     | Back to `queued` with a delay                                                                         |
| `request_approval`      | `(p_task uuid, p_worker text, p_reason text, p_details jsonb) → boolean`              | Sets `waiting_for_user` and the pending approval                                                      |
| `resume_task`           | `(p_task uuid, p_user uuid, p_answer jsonb) → boolean`                                | Stores the answer in `payload.user_answer`, clears the request, re-queues                             |
| `approve_task`          | `(p_task uuid, p_user uuid, p_note text) → boolean`                                   | **Merges** `approved_at`/`note` into `approval`, keeps `details`, re-queues                           |
| `cancel_task`           | `(p_task uuid, p_user uuid) → boolean`                                                | Cancels any non-final task owned by the user                                                          |
| `consume_rate_limit`    | `(p_key text, p_limit integer, p_window_seconds integer) → boolean`                   | One upsert; false when the window is full                                                             |
| `reserve_llm_tokens`    | `(p_user uuid, p_amount integer, p_cap bigint) → boolean`                             | One conditional update; false when it would exceed the daily cap                                      |
| `settle_llm_tokens`     | `(p_user uuid, p_reserved integer, p_actual integer) → void`                          | Refunds or charges the difference                                                                     |
| `set_updated_at`        | trigger                                                                               | Maintains `updated_at`                                                                                |
| `handle_new_auth_user`  | trigger on `auth.users`                                                               | Mirrors the user into `public.users`, seeds `budget_counters`                                         |

## Data and storage

| Table             | Owner column | Purpose                                     |
| ----------------- | ------------ | ------------------------------------------- |
| `users`           | `id`         | Mirror of `auth.users`                      |
| `user_profiles`   | `user_id`    | Applicant data and resume pointers          |
| `tasks`           | `user_id`    | Durable queue and progress                  |
| `jobs`            | `user_id`    | Listings found by discovery, with `task_id` |
| `documents`       | `user_id`    | Reserved for generated documents            |
| `llm_usage_log`   | `user_id`    | Per-call token accounting                   |
| `budget_counters` | `user_id`    | Daily used/limit counters                   |
| `rate_limits`     | `key`        | Fixed-window counters, service role only    |

RLS is enabled on all of them with per-user policies. `llm_usage_log`,
`budget_counters` and `rate_limits` are not writable by users.

Storage: bucket `resumes`, private, 10 MB, `application/pdf` only. Object names are
`<user_id>/<uuid>.pdf`, generated server-side. The web app only ever sees a 60
second signed URL. Browser session state lives in `.browser-state/<user_id>.json`
on the worker host, mode 0600 inside a 0700 directory, outside the database and
never served.

## Key dependencies

`@vanguard/server`: `hono`, `@hono/node-server`, `@supabase/supabase-js`,
`@supabase/server` (JWKS token verification), `postgres`, `drizzle-orm`,
`playwright`, `ai`, `@ai-sdk/google`, `zod`, `@vanguard/contracts`.

`@vanguard/web`: `@sveltejs/kit`, `svelte`, `@supabase/ssr`,
`@supabase/supabase-js`, `zod`, `@vanguard/contracts`.

Tooling: `typescript`, `tsx`, `vitest`, `eslint`, `prettier`, `drizzle-kit`
(introspection only), `svelte-check`. Node 22 or newer is required by
`@supabase/server`.
