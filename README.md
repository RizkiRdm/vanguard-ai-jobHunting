# Vanguard

AI job hunting assistant. It searches public job listings, prepares application
material, and fills in application forms in a real browser. It never submits an
application without explicit approval from the user.

Stack: SvelteKit (web) · Hono on Node.js (API + worker) · Playwright (browser) ·
Supabase Postgres, Auth and private Storage · Zod contracts · TypeScript strict.

## Requirements

- Node.js 20 or newer
- A Supabase project (Postgres, Auth, Storage)
- A Gemini API key
- Playwright Chromium: `npx playwright install chromium --with-deps`

## Setup

```bash
npm install
cp .env.example .env      # fill in real values
npm run db:migrate        # applies supabase/migrations/*.sql
```

Create the `resumes` bucket with `npm run db:migrate` (the migration inserts it)
and enable email confirmation in Supabase Auth if you want verified sign-ups.

## Development

Run each in its own terminal:

```bash
npm run dev:web      # http://localhost:5173
npm run dev:server   # http://localhost:8000
npm run worker       # background task worker
```

The browser talks only to SvelteKit. SvelteKit holds the Supabase session in
HttpOnly cookies and forwards requests to the Hono API with a bearer token.

## Checks

```bash
npm run typecheck
npm run lint
npm test
npm run build
```

The web build and start require `PUBLIC_SUPABASE_URL`, `PUBLIC_SUPABASE_ANON_KEY`
and `API_BASE_URL`; `src/env.ts` validates them and fails on missing values.

The SQL layer has an integration test that only runs against a real database:

```bash
# any Postgres 15+ with the Supabase auth/storage stubs applied
psql "$TEST_DATABASE_URL" -f supabase/local-stub.sql
npm run db:migrate
TEST_DATABASE_URL=postgres://... npx vitest run apps/server/src/modules/tasks/repository.integration.test.ts
```

It covers atomic task claiming, lease ownership, the approval flow and per-user
isolation. Without `TEST_DATABASE_URL` the file is skipped.

## Architecture

- `apps/web` — SvelteKit UI, session cookies, server load functions and form actions.
- `apps/server` — Hono API (`src/api.ts`) and worker (`src/worker.ts`), same codebase,
  separate processes.
- `packages/contracts` — Zod schemas shared by both sides.
- `supabase/migrations` — schema, SQL functions for task claiming, rate limiting and
  token budget, plus Row Level Security policies.

Task lifecycle: `queued → running → (waiting_for_user) → succeeded | failed | cancelled`.
Workers claim tasks with `SELECT … FOR UPDATE SKIP LOCKED`, hold a lease with a
heartbeat, and expired leases are requeued. Retries are bounded with backoff.

The AI agent can click, fill, select and upload. When the form looks submittable it
returns `ready_to_submit`; the task parks as `waiting_for_user` and nothing is
submitted until the user approves it in the UI.

Details: `docs/ARCHITECTURE.md`. Audit of the code it replaced: `docs/AUDIT.md`.

## Deployment

Two long-running Node processes and one static/server-rendered frontend:

```bash
npm run build                    # apps/web -> apps/web/build
node apps/web/build              # web
npx tsx apps/server/src/api.ts   # API
npx tsx apps/server/src/worker.ts
```

Supabase hosts the database, auth and file storage; it does not run the browser
worker. Use a host that keeps a process alive and allows Chromium (memory ≥1 GB,
`--no-sandbox` is already set for containers). Set `WEB_ORIGIN` to the real
frontend origin so CORS stays narrow, and keep `SUPABASE_SERVICE_ROLE_KEY` on the
server only.
