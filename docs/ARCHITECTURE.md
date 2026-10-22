# Architecture

## Processes

| Process | Entry point                          | Job                                                          |
| ------- | ------------------------------------ | ------------------------------------------------------------ |
| Web     | `apps/web` (SvelteKit, adapter-node) | UI, Supabase session cookies, server-side calls to the API   |
| API     | `apps/server/src/api.ts`             | HTTP routes, authentication, validation                      |
| Worker  | `apps/server/src/worker.ts`          | Claims tasks, runs Playwright and Gemini, updates task state |

API and worker share one package and one deployment image but start separately,
so a browser-heavy worker cannot block HTTP traffic and each can be restarted or
scaled on its own.

The browser never calls the API directly. SvelteKit server code holds the Supabase
access token from the HttpOnly cookie and forwards it as a bearer token. No token
appears in a URL, and client JavaScript never reads the cookie.

## Layers

```text
HTTP route (Hono)  →  auth + Zod validation  →  service  →  repository  →  Postgres
                                                   ↘  infrastructure (browser, AI, storage)
```

- `src/modules/*/routes.ts` — HTTP concerns only.
- `src/modules/*/service.ts` — business rules; testable without Hono.
- `src/modules/*/repository.ts` — Drizzle queries over `postgres.js`; SQL functions
  are called with `sql` templates. No queries in routes.
- `src/db/schema.ts` — typed mirror of the SQL migrations, for query typing only.
- `src/infrastructure/` — Playwright sessions, Gemini calls, prompts.
- `packages/contracts` — Zod schemas and inferred types shared by web and server.

## Data model

`users` mirrors `auth.users`. `user_profiles` holds the applicant data used to fill
forms. `resumes` live in a private Storage bucket; the profile stores only the
object path. `tasks` is the durable queue. `jobs` stores listings actually found by
a discovery task. `llm_usage_log` and `budget_counters` account for token spend.
`rate_limits` backs fixed-window limits.

Every user-owned table has RLS policies for `auth.uid()`, but the API also uses the
secret key, so repository queries filter on `user_id` explicitly. RLS is a
backstop, not the authorization.

## Supabase project

Postgres, Auth and Storage are Supabase-managed; the API and worker connect to
Postgres with `DATABASE_URL` and use the secret key only for Storage and
token verification. The browser uses the publishable key for sign-in and gets resume
access through short-lived signed URLs.

Migrations are plain SQL files in `supabase/migrations`, applied in filename order
and recorded in `public.schema_migrations` by `npm run db:migrate`. Supabase also
keeps its own migration history when changes are applied through the dashboard or
the CLI, so pick one path per environment and keep the two records identical.

Drizzle is the query layer, not the migration tool. `drizzle-kit` can describe
tables, but not RLS policies, `WITH CHECK` clauses, triggers, `SECURITY DEFINER`
functions, grants or the Storage bucket, and `drizzle-kit migrate` keeps its own
journal. Letting it own this schema would either drop the security model or re-run
DDL that is already applied. `supabase/migrations` stays the source of truth and
`apps/server/src/db/schema.ts` mirrors it for types only; see
[REFERENCE.md](REFERENCE.md#sql-functions) for the function list.

RLS and grants are part of the security model:

- Policies are declared `to authenticated` with both `using` and `with check`, so a
  user cannot read another user's rows or reassign ownership.
- `(select auth.uid())` is used so the check is evaluated once per statement.
- Supabase grants EXECUTE on new public functions to `anon` and `authenticated` by
  default. The queue, budget and rate-limit functions are revoked from those roles
  and granted to `service_role` only; their `search_path` is pinned.
- The `resumes` bucket is private, PDF-only, 10 MB, with a policy keyed on the
  first folder segment matching `auth.uid()`.

## Task lifecycle

```text
queued ──claim──▶ running ──finish──▶ succeeded
  ▲                  │
  │                  ├── request_approval ──▶ waiting_for_user ──approve/resume──▶ queued
  │                  ├── retry (bounded, backoff) ──▶ queued
  │                  └── retries exhausted ──▶ failed
  └── reclaim_expired_tasks (lease expired, attempts left)
cancelled from any non-final state by the owner
```

- `claim_task` uses `SELECT … FOR UPDATE SKIP LOCKED`, so two workers cannot take the
  same row.
- Each claim sets `lease_expires_at`; the worker heartbeats at one third of the lease.
- A crashed worker's lease expires and `reclaim_expired_tasks` requeues it.
- `finish_task` and `request_approval` require the caller's `worker_id` and
  `status = 'running'`, so a stale worker cannot overwrite newer state.
- `tasks.approval` holds either a pending request (`reason`, `details`) or an
  approval (`approved_at`, `note`). The agent captures the submit selector but does
  not click it; after approval the worker clicks that selector.

## Browser automation

`openSession(userId)` launches Chromium with a per-user context and stored
`storageState` in `.browser-state/` (directory 0700, file 0600, never served).
No remote debugging port is exposed and Playwright objects never leave the worker.

`runApplication` loops screenshot → `generateJson(AiDecision)` → dispatch, bounded
by `maxSteps`. Page text is untrusted: the system prompt forbids following
instructions in the page, revealing secrets, bypassing CAPTCHA, and submitting.

Discovery navigates DuckDuckGo HTML results and reads only listing links and
snippets that exist in the DOM. If nothing is found, the task succeeds with zero
jobs; nothing is fabricated.

## Cost control

`reserve_llm_tokens(user, amount, cap)` performs one conditional UPDATE with the
daily counter reset, so parallel requests cannot both pass the check.
`generateJson` reserves, calls the model, then settles the real usage in `finally`
and appends to `llm_usage_log`. Over-budget calls fail with 429.

## Failure behaviour

- Missing or malformed env vars abort startup with the field names listed.
- Unhandled errors log server-side and return `{ error: { code, message } }` with no
  stack trace.
- `failed` tasks carry a redacted error summary the UI can show.
- Expired logins or CAPTCHA stop the workflow and park the task for a human.

## Known limits

- Rate limiting and token budget are fixed-window and global per key; fine for a
  single-user tool, revisit for multi-tenant use.
- Screenshots are transient worker artifacts and are not stored or served.
- Resume parsing is not automated; the profile is filled in manually.
- The schema, RLS policies, grants and the private `resumes` bucket are applied to
  one hosted Supabase project. Task, browser and AI behaviour was exercised only
  against a local Postgres, so no hosted end-to-end run is verified.
- Discovery depends on DuckDuckGo's HTML results; it is a scrape and can break
  without notice.
