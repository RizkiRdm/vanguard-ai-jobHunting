# Vanguard

An AI job hunting assistant. It discovers real job listings, prepares application
material from your profile, and fills in application forms in a real browser. It
stops before submitting and waits for your approval.

> **Status: MVP, not deployed.** The schema, RLS policies and storage bucket are
> applied to one hosted Supabase project and the API, worker and web app run
> locally. No browser workflow has been exercised against a live job site yet, and
> nothing is hosted. See [docs/AUDIT.md](docs/AUDIT.md) for what is proven and what
> is not.

## What it does

- **Discovery** — searches DuckDuckGo's HTML results for a query and stores the
  listings it actually saw. Nothing is invented; an empty result stays empty.
- **Applications** — opens the listing in Playwright, decides each step from a
  screenshot, and fills fields using your profile and resume. The model is never
  allowed to click submit.
- **Approval gate** — when the form is filled, the task parks in
  `waiting_for_user` and shows you the step it wants to take. Only your approval
  re-queues it, and only then does the worker click the captured submit selector.
- **Durable tasks** — every task lives in Postgres, is claimed with
  `SELECT … FOR UPDATE SKIP LOCKED`, and holds a lease. A crashed worker's task is
  reclaimed, retried with backoff, or failed after the attempt limit.

## Stack

| Layer      | Choice                                                         |
| ---------- | -------------------------------------------------------------- |
| Web        | SvelteKit 3, Svelte 5, TypeScript strict                       |
| API + jobs | Hono on Node.js 22, separate API and worker entry points       |
| Database   | Supabase Postgres, Drizzle as the query layer, SQL migrations  |
| Auth       | Supabase Auth; server verifies tokens against the project JWKS |
| Files      | Supabase Storage, private bucket, signed URLs only             |
| Browser    | Playwright (Chromium)                                          |
| AI         | Google Gemini, JSON-validated responses, token budget          |

The web app never calls the API from the browser: SvelteKit server code holds the
session cookie and forwards requests with the user's bearer token.

## Five minute path

```bash
npm install
cp .env.example .env      # fill in Supabase, Gemini and the pooler URL
npm run db:migrate        # applies supabase/migrations/*.sql in order
```

Then, in three terminals:

```bash
npm run dev:web           # http://localhost:5173
npm run dev:server        # http://localhost:8000
npm run worker            # browser + AI work
```

Create an account on the login page, fill in your profile, upload a PDF resume,
then start a discovery task from the dashboard.

Full instructions, including how to get each environment value: [docs/SETUP.md](docs/SETUP.md).

## Checks

```bash
npm run typecheck         # tsc (server) + svelte-check (web)
npm run lint              # eslint
npm test                  # vitest
npm run build             # adapter-node build of the web app
```

All four pass on the current commit. The database integration tests skip unless
`TEST_DATABASE_URL` points at a Postgres with `supabase/local-stub.sql` applied.

## Layout

```
apps/web/                SvelteKit UI (routes, server actions, session cookie)
apps/server/src/         Hono API, worker, modules, infrastructure
packages/contracts/      Zod schemas and types shared by web and server
supabase/migrations/     schema, SQL functions, RLS policies, storage bucket
supabase/local-stub.sql  auth/storage stubs so migrations run on plain Postgres
docs/                    setup, architecture, reference, audit
```

## Security model

- Identity comes only from a verified Supabase access token checked against the
  project JWKS. A user id in a body, query string or header is never trusted.
- Every user-owned query filters on the authenticated user id; the secret key
  bypasses RLS, so RLS is a backstop, not the authorization.
- Resumes are validated by size, MIME type and `%PDF-` magic bytes, stored under a
  server-generated name in a private bucket, and served through 60 second signed
  URLs.
- Browser state in `.browser-state/` is credentials: gitignored, never served, never
  logged.
- Page content and job descriptions are untrusted input. They cannot change agent
  rules, reveal secrets or trigger unrelated actions.
- No hardcoded or fallback secrets; a missing variable aborts startup.

## Documentation

- [docs/SETUP.md](docs/SETUP.md) — install, configure, migrate, run, troubleshoot
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — how the pieces fit and why
- [docs/REFERENCE.md](docs/REFERENCE.md) — endpoints, environment variables, SQL functions
- [docs/AUDIT.md](docs/AUDIT.md) — what the Python version got wrong and how it was fixed
- [AGENTS.md](AGENTS.md) — rules for coding agents working in this repository
