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
- `src/modules/*/repository.ts` — tagged-template SQL (`postgres.js`), never raw
  queries in routes.
- `src/infrastructure/` — Playwright sessions, Gemini calls, prompts.
- `packages/contracts` — Zod schemas and inferred types shared by web and server.

## Data model

`users` mirrors `auth.users`. `user_profiles` holds the applicant data used to fill
forms. `resumes` live in a private Storage bucket; the profile stores only the
object path. `tasks` is the durable queue. `jobs` stores listings actually found by
a discovery task. `llm_usage_log` and `budget_counters` account for token spend.
`rate_limits` backs fixed-window limits.

Every user-owned table has RLS policies for `auth.uid()`, but the API also uses the
service-role key, so repository queries filter on `user_id` explicitly. RLS is a
backstop, not the authorization.

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
