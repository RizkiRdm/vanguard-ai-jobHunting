# Vanguard

An AI job hunting assistant that finds real job listings, drafts application
material, and fills in application forms in a real browser — then stops and waits
for you to approve the submission.

Vanguard is not an auto-applier. The agent can click, type, select and upload a
resume, but the task parks as `waiting_for_user` the moment a form looks
submittable. Nothing leaves your account until you approve it.

> [!NOTE]
> Status: MVP. The stack, schema and API are complete; the project is not deployed
> and the browser flows have not been exercised against live job sites. See
> [`docs/AUDIT.md`](docs/AUDIT.md) for what is proven and what is not.

## What it does

- **Discover jobs** — a Playwright task searches public listings and stores the
  results it actually saw. No invented companies, titles or salaries.
- **Prepare an application** — a Gemini-driven agent reads the page, fills the
  visible form fields, and stops at the submit button.
- **Ask before submitting** — the task pauses with a reason and the details the
  agent found; approving it from the UI is the only way the submission proceeds.
- **Stay recoverable** — every task lives in Postgres, claims atomically, holds a
  lease with a heartbeat, and is requeued if a worker dies.
- **Control cost** — per-user daily token budget and per-user rate limits are
  enforced by single SQL statements, so concurrent requests cannot overspend.

## Stack

| Layer     | Choice                                                         |
| --------- | -------------------------------------------------------------- |
| Web       | SvelteKit 3, Svelte 5, TypeScript strict                       |
| API       | Hono on Node.js                                                |
| Worker    | Same codebase, separate process, Postgres-backed queue         |
| Browser   | Playwright Chromium                                            |
| Database  | Supabase Postgres — schema, RLS, SQL functions for the queue   |
| Auth      | Supabase Auth, session in HttpOnly cookies via `@supabase/ssr` |
| Storage   | Supabase Storage, private `resumes` bucket, signed URLs        |
| AI        | Google Gemini (`@google/genai`)                                |
| Contracts | Zod schemas shared by web and server                           |

## Architecture

```text
browser ──► SvelteKit (session cookie, auth guard)
              │  bearer token
              ▼
            Hono API ──► Postgres ◄── Worker ──► Playwright ──► job site
              │            │  ▲         │
              └────────────┘  └─────────┘  └──► Gemini (structured JSON)
                   Supabase Auth / Storage
```

- The browser never talks to the API directly and never sees a token in a URL.
- The API and worker share code but run as separate processes; only the worker
  runs Chromium.
- Business rules live in services, SQL lives in repositories, route handlers stay
  thin. Shared request/response shapes live in `packages/contracts`.

Task lifecycle:

```text
queued ──► running ──► succeeded
              │  ▲
              │  └── waiting_for_user ──► queued   (approval or answer)
              └──► failed / cancelled
```

Workers claim with `SELECT … FOR UPDATE SKIP LOCKED`, renew a lease while working,
and `reclaim_expired_tasks()` requeues anything abandoned. Retries are bounded
with backoff.

## Requirements

- Node.js 22 or newer (`@supabase/server` requires it)
- A Supabase project (Postgres, Auth, Storage)
- A Gemini API key
- Chromium for Playwright: `npx playwright install chromium --with-deps`

## Setup

```bash
npm install
cp .env.example .env      # then fill in the values
npm run db:migrate        # schema, SQL functions, RLS, private resumes bucket
```

Full details, including the exact environment variables and how to provision the
database with or without the Supabase CLI, are in [`docs/SETUP.md`](docs/SETUP.md).

> [!IMPORTANT]
> `apps/web/src/env.ts` validates `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`
> and `API_BASE_URL` at build and start time. A missing value fails on purpose; no
> fallback secrets exist anywhere in this project.

## Development

Three processes, three terminals:

```bash
npm run dev:web      # http://localhost:5173
npm run dev:server   # http://localhost:8000
npm run worker       # background task worker (needs Chromium)
```

## Checks

```bash
npm run typecheck    # tsc -p apps/server && svelte-check
npm run lint
npm test             # vitest
npm run build        # SvelteKit production build
```

The SQL layer has an integration test that runs only against a real database:

```bash
psql "$TEST_DATABASE_URL" -f supabase/local-stub.sql
npm run db:migrate
TEST_DATABASE_URL=postgres://... npx vitest run \
  apps/server/src/modules/tasks/repository.integration.test.ts
```

It covers atomic claiming, lease ownership, the approval flow and per-user
isolation. Without `TEST_DATABASE_URL` the file is skipped.

## Security notes

- Identity is taken only from a verified Supabase access token. A user id in a
  body, query string or header is never treated as proof of identity.
- Every user-owned query filters on the authenticated user id. The secret key
  bypasses RLS, so RLS is defence in depth, not the authorization layer.
- Row Level Security is enabled on all user tables, policies are scoped
  `to authenticated` and include `WITH CHECK`.
- `EXECUTE` on the queue, budget and rate-limit functions is revoked from `anon`
  and `authenticated`; only `service_role` can call them.
- Resumes are PDF-only, capped at 10 MB, checked for the `%PDF-` magic bytes,
  stored under server-generated names in a private bucket, and served through
  short-lived signed URLs.
- Browser session state lives in `.browser-state/` (credentials, gitignored) and is
  never served, logged or committed.
- Page content is treated as untrusted input and cannot change the agent's rules.

## Deployment

Two long-running Node processes plus the web app:

```bash
npm run build                    # apps/web -> apps/web/build
node apps/web/build              # web
npx tsx apps/server/src/api.ts   # API
npx tsx apps/server/src/worker.ts
```

Supabase hosts Postgres, Auth and Storage; it does not run the browser worker. Use
a host that keeps a process alive and allows Chromium (1 GB RAM minimum, writable
`.browser-state/`), set `WEB_ORIGIN` to the real frontend origin, and keep
`SUPABASE_SECRET_KEY` server-side only. Nothing has been deployed yet.

## Documentation

- [`docs/SETUP.md`](docs/SETUP.md) — provisioning, environment, troubleshooting
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — processes, data model, task queue, browser rules
- [`docs/AUDIT.md`](docs/AUDIT.md) — defects found in the Python implementation and what replaced them
- [`AGENTS.md`](AGENTS.md) — rules, guardrails and gotchas for humans and AI agents
