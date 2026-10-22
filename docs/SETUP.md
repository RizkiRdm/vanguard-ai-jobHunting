# Setup

How to get Vanguard running locally against a Supabase project. Written for the
first run; if a step behaves differently than described, the code in `apps/server`
and `supabase/migrations` wins.

## 1. Prerequisites

- Node.js 22 or newer (`node -v`) — `@supabase/server` requires it
- A Supabase project with Auth enabled
- A Gemini API key from Google AI Studio
- Chromium for Playwright

```bash
npm install
npx playwright install chromium --with-deps
```

## 2. Environment

```bash
cp .env.example .env
```

Fill in:

| Variable                   | Where to get it                                             | Notes                                                                                                                                                    |
| -------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `DATABASE_URL`             | Supabase → Project settings → Database → Connection pooling | Use the pooler host and port (`:6543` transaction or `:5432` session) with `?sslmode=require`. The direct `db.<ref>` host is IPv6-only on many networks. |
| `SUPABASE_URL`             | Project settings → API                                      | `https://<project-ref>.supabase.co`                                                                                                                      |
| `SUPABASE_PUBLISHABLE_KEY` | Project settings → API keys                                 | `sb_publishable_…`. Safe in the browser; RLS decides what it can read                                                                                    |
| `SUPABASE_SECRET_KEY`      | Project settings → API keys                                 | `sb_secret_…`. Server only, bypasses RLS, never in web env or bundles                                                                                    |
| `SUPABASE_JWKS_URL`        | `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`   | Public. The API verifies access tokens against these keys locally, no Auth call per request                                                              |
| `GEMINI_API_KEY`           | Google AI Studio                                            | Server only                                                                                                                                              |
| `API_BASE_URL`             | You                                                         | `http://localhost:8000` locally, the API origin in production                                                                                            |
| `WEB_ORIGIN`               | You                                                         | Must match the frontend origin exactly, it drives CORS                                                                                                   |

`SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` are also read by the web app (marked
`public: true` in `apps/web/src/env.ts`), so the browser can sign in. Every other
value stays server-side.

`apps/server/src/config/env.ts` and `apps/web/src/env.ts` validate these with Zod
and abort startup on anything missing or malformed. There are no fallback secrets.

## 3. Database

The schema, SQL functions and RLS policies live in `supabase/migrations` and are
applied in filename order. A fresh Supabase project needs the steps below; the
project referenced by `.env` already has them.

```bash
npm run db:migrate
```

The runner records applied files in `public.schema_migrations`, so re-running it is
safe. It is not an Alembic-style downgrade tool; to undo something, write a new
migration.

Queries go through Drizzle (`apps/server/src/db/schema.ts` mirrors these tables for
typing). The SQL files stay authoritative: RLS, triggers and the queue functions
cannot be expressed in Drizzle, so do not use `drizzle-kit push`.

If you can reach the project only through the Supabase dashboard, paste each file
into the SQL editor in filename order. If you do that, `public.schema_migrations`
is not written, so a later `npm run db:migrate` will try to apply the same DDL
again and fail. Prefer the pooler URL and the command above.

What the migrations create:

- `users` mirrors `auth.users` through the `on_auth_user_created` trigger, and
  seeds a `budget_counters` row for each new user.
- `user_profiles`, `tasks`, `jobs`, `documents`, `llm_usage_log`,
  `budget_counters`, `rate_limits`.
- SQL functions for task claiming, heartbeats, finishing, retries, approval,
  cancellation, rate limiting and token budget reservation.
- Row Level Security on every user-owned table, plus a private `resumes` bucket
  with a 10 MB / PDF-only limit.

### Plain Postgres for tests

Integration tests need a database with the Supabase schemas stubbed:

```bash
docker run -d --name vanguard-pg -e POSTGRES_PASSWORD=pw -p 5433:5432 postgres:16
psql postgres://postgres:pw@127.0.0.1:5433/postgres -f supabase/local-stub.sql
TEST_DATABASE_URL=postgres://postgres:pw@127.0.0.1:5433/postgres \
  npx vitest run apps/server/src/modules/tasks/repository.integration.test.ts
```

`local-stub.sql` creates the `auth`/`storage` schemas, `auth.uid()`, and the
`anon`/`authenticated`/`service_role` roles. It is for tests only.

## 4. Supabase Auth

- Email/password is the only enabled provider.
- For local development you can turn off "Confirm email" so sign-up returns a
  session immediately; keep it on in production.
- Users are created through the UI at `/login`. There is no admin endpoint and no
  way to mint a token, by design.

## 5. Run it

Three processes, three terminals:

```bash
npm run dev:server   # Hono API on :8000
npm run dev:web      # SvelteKit on :5173
npm run worker       # claims tasks, drives Chromium
```

Open `http://localhost:5173`, sign up, fill in the profile, upload a PDF resume,
then create a discovery task. The worker picks it up within `WORKER_POLL_MS`.

## 6. Verify the setup

```bash
npm run typecheck
npm run lint
npm test
npm run build
```

Runtime checks:

```bash
curl -s localhost:8000/health   # {"status":"operational"}
curl -s localhost:8000/ready    # 200 when the database answers, 503 otherwise
```

Create a discovery task from the UI. A task that stays `queued` means the worker
is not running or cannot reach the database; check its log output first.

## 7. Common problems

| Symptom                                | Cause                                                                | Fix                                                                                         |
| -------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Startup lists missing env fields       | Zod env validation                                                   | Fill those fields in `.env`; nothing is defaulted                                           |
| `/ready` returns 503                   | `DATABASE_URL` wrong, password not set, or pooler region wrong       | Copy the pooler string from the dashboard, keep `?sslmode=require`                          |
| Upload returns 415                     | File is not a real PDF                                               | The server checks the `%PDF-` header, not just the extension                                |
| Task stuck in `queued`                 | Worker down, or lease logic never ran                                | Start `npm run worker`; after `TASK_LEASE_SECONDS` a stale claim is requeued                |
| Task stuck in `running`                | Worker died mid-task                                                 | Wait for the lease to expire; `reclaim_expired_tasks` requeues it, then retries are bounded |
| Browser fails to launch in a container | Missing shared libraries or sandbox                                  | `npx playwright install --with-deps chromium`; `--no-sandbox` is already passed             |
| Web build fails on env                 | `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY` or `API_BASE_URL` missing | Set them in the build environment; `apps/web/src/env.ts` validates at build and start       |
| 401 from the web app                   | Session cookie expired                                               | Sign in again; tokens are short lived and there is no refresh-token design yet              |

## 8. Deployment notes

Supabase hosts Postgres, Auth and Storage. It does not run the browser worker.

Deploy three things:

1. The API: `npx tsx apps/server/src/api.ts`
2. The worker: `npx tsx apps/server/src/worker.ts`
3. The web app: `npm run build` then `node apps/web/build`

Requirements: a host that keeps Node processes alive, at least 1 GB RAM for
Chromium, and a writable directory for `.browser-state/` (or accept that sessions
do not survive restarts). Set `WEB_ORIGIN` to the deployed frontend origin.

Nothing in this repository has been deployed yet. Treat deployment steps as
instructions, not as verified results.
