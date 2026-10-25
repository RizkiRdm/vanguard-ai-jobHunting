# Vanguard AI Job Hunting — Project Memory

**Last updated:** 2026-10-25 | **Commit:** `d329c31` (main) | **Branch:** main

---

## Project Overview

Vanguard is an AI job hunting assistant that discovers real job listings, prepares application materials, and fills in application forms in a browser. **Never submits without explicit user approval.**

**Status:** MVP — schema/RLS/bucket applied to one hosted Supabase project. API/worker/web run locally. **Nothing deployed. No live job-site run. No real user session.**

---

## Stack (Locked)

| Layer | Technology |
|-------|------------|
| Frontend | SvelteKit 3 + Svelte 5 + TypeScript |
| API | Hono on Node.js 22+ |
| Browser | Playwright (Chromium) |
| Database | Supabase PostgreSQL (Postgres 16) |
| Auth | Supabase Auth (JWT verification via `@supabase/server` + JWKS) |
| Storage | Supabase Storage (private `resumes` bucket, 10 MB, PDF only) |
| Query Layer | Drizzle ORM over `postgres.js` (SQL remains authoritative) |
| Migrations | Plain SQL in `supabase/migrations/` applied via `npm run db:migrate` |
| AI | Gemini (`@google/genai`) with JSON validation + token budget |
| Contracts | Zod in `packages/contracts` (shared server/web) |
| Testing | Vitest (unit), integration tests need `TEST_DATABASE_URL` |

---

## Repository Structure

```
apps/
  web/              # SvelteKit frontend
    src/
      routes/       # file-based routes (+page.server.ts load/actions)
      lib/server/api.ts   # ONLY place calling Hono API
      hooks.server.ts     # Supabase session cookies + auth guard
      env.ts              # $app/env/public + private (Zod)
  server/           # Hono API + worker
    src/
      api.ts          # API entry point (port 8000)
      worker.ts       # Worker entry point (background tasks)
      app.ts          # Hono factory: middleware, mounts, CORS
      config/env.ts   # Zod env validation (fail-fast, no fallbacks)
      lib/
        db.ts         # postgres.js pool + Drizzle (prepare:false)
        supabase.ts   # getAdminClient() (service role, bypasses RLS)
        logger.ts     # Redacting JSON logger
        errors.ts     # AppError + helpers
      modules/
        tasks/        # routes.ts → service.ts → repository.ts
        jobs/
        profile/
        resumes/
        health/
      infrastructure/
        ai/           # gemini.ts, prompts.ts (AiDecision Zod)
        browser/      # session.ts, discovery.ts, application.ts
    scripts/migrate.ts  # Applies supabase/migrations/*.sql in order
packages/contracts/  # Shared Zod schemas + types
supabase/migrations/ # 6 SQL files (init, task_queue, rls, function_grants, hardening, trigger_grant)
supabase/local-stub.sql  # Auth/storage stubs for plain Postgres tests
docs/
  README.md         # Explanation + entry point
  SETUP.md          # How-to (prereqs, env, migrations, 3 processes, troubleshooting)
  ARCHITECTURE.md   # Processes, layers, data model, lifecycle, limits
  REFERENCE.md      # Scripts, env vars, HTTP API, task states, SQL functions, storage
  AUDIT.md          # Legacy defects, fixes, verification evidence, not-claimed
  AGENTS.md         # Rules for agents (this file's rules)
```

---

## What's Done (Verified)

- ✅ Full TypeScript migration from Python/FastAPI
- ✅ Hono API with auth (`verifyAuth` from `@supabase/server`), rate limits, error handling
- ✅ Drizzle query layer over `postgres.js` (transaction pooler, `prepare:false`)
- ✅ Supabase Auth with JWKS verification (`SUPABASE_JWKS_URL`)
- ✅ 6 SQL migrations applied to hosted project via pooler URL (`:6543`)
- ✅ RLS policies on all user tables + `resumes_own` storage policy
- ✅ Function grants: `anon` blocked, `service_role` allowed, `search_path` pinned
- ✅ Private `resumes` bucket (PDF, 10 MB)
- ✅ Task queue: atomic claim (`SKIP LOCKED`), leases, heartbeat, reclaim, retry, approval gate
- ✅ Browser automation: per-user contexts, `.browser-state/` (0700/0600), no CDP exposure
- ✅ AI: `generateJson` with Zod validation, token reservation + settlement, budget 429
- ✅ SvelteKit web: login, profile, resume upload, task list/detail, discovery/apply forms, polling
- ✅ Shared contracts (`packages/contracts`)
- ✅ All gates green: typecheck, lint, format, 10 unit tests (4 DB tests skipped without `TEST_DATABASE_URL`)
- ✅ Documentation rewrite (Diátaxis): README, SETUP, ARCHITECTURE, REFERENCE, AUDIT, AGENTS
- ✅ Git: `main` at `d329c31`, `feature/ts-hono-migration` pushed, recovery branch/tags local only

---

## Critical Blockers / Unverified

| Area | Blocker | Resolution Needed |
|------|---------|-------------------|
| **Credentials** | Real `SUPABASE_SECRET_KEY`, DB password, publishable key were in `.env.example` locally (never committed, now placeholders) | Rotate `SUPABASE_SECRET_KEY` in dashboard |
| **Wrong project residue** | Empty `resumes` bucket on `orjicvxvqrvrazazclha` (cannot delete via SQL, `storage.protect_delete`) | Delete in that project's dashboard → Storage |
| **Auth E2E** | Only 401 path verified; no real signed-in user token tested | Sign up/in via `/login`, call `/tasks` with real token |
| **Cross-account isolation** | Not tested at runtime | Second account cannot read first's task/resume (expect 404) |
| **DB integration tests** | 4 tests skipped (need `TEST_DATABASE_URL`) | Run against real DB or decide CI strategy |
| **Discover task** | Never run against live DuckDuckGo + Gemini | One end-to-end: queued → running → succeeded |
| **Apply task** | Never run to approval gate | One end-to-end: stops at `waiting_for_user`, approve re-queues with `submit_selector` |
| **Token budget** | 429 path not tested live | Exceed `DAILY_TOKEN_BUDGET`, confirm 429 + `llm_usage_log` entry |
| **Playwright** | Chromium launch + `.browser-state/` perms not verified on target | `npx playwright install --with-deps chromium` |
| **CI** | Never ran on GitHub Actions | Push, confirm typecheck/lint/format/test/build pass |
| **Deployment** | No host chosen for long-lived Node + Chromium | Decide before any deploy work |

---

## Key Architectural Decisions

1. **SQL is authoritative** — `drizzle-kit migrate`/`push` NOT used. RLS, triggers, grants, bucket cannot be expressed in Drizzle schema. Migrations applied via `npm run db:migrate` (idempotent per filename).
2. **Drizzle = query types only** — `src/db/schema.ts` mirrors tables for typing. JSONB cast as `${JSON.stringify(v)}::jsonb`.
3. **Transaction pooler required** — Direct host is IPv6-only. `DATABASE_URL` must be `postgresql://postgres.<ref>:<pw>@aws-0-<region>.pooler.supabase.com:6543/postgres` with `prepare:false`.
4. **Auth via JWKS** — `verifyAuth` from `@supabase/server` validates tokens locally against `SUPABASE_JWKS_URL`. No per-request Auth API call.
5. **Approval gate** — AI action `ready_to_submit` NEVER clicks. Task parks via `request_approval`; only explicit user `approve` re-queues, then worker clicks captured `submit_selector`.
6. **No fabricated data** — Discovery scrapes DuckDuckGo HTML; empty results = honest empty state.
7. **Service role bypasses RLS** — Every repository query filters on `user_id` explicitly. RLS is a backstop.
8. **`.browser-state/` = credentials** — Gitignored, never served, never logged.

---

## Commands

```bash
npm install
cp .env.example .env          # Fill real values (see SETUP.md)
npm run db:migrate            # Apply 6 SQL files (idempotent)
npm run dev:web               # http://localhost:5173
npm run dev:server            # http://localhost:8000
npm run worker                # Background task worker

npm run typecheck             # tsc + svelte-check
npm run lint
npm test                      # vitest (10 pass, 4 skipped)
npm run build                 # Web production build
npm run format:check
```

---

## Environment Variables (Required)

**Server (`.env`):**
- `DATABASE_URL` — Pooler URL (port 6543, `prepare:false`)
- `SUPABASE_URL` — `https://<ref>.supabase.co`
- `SUPABASE_PUBLISHABLE_KEY` — `sb_publishable_...` (client-side, RLS-bound)
- `SUPABASE_SECRET_KEY` — `sb_secret_...` (server-side, bypasses RLS)
- `SUPABASE_JWKS_URL` — `https://<ref>.supabase.co/auth/v1/.well-known/jwks.json`
- `GEMINI_API_KEY` — Gemini API key

**Web (validated at build/start by `apps/web/src/env.ts`):**
- `SUPABASE_URL` (same)
- `SUPABASE_PUBLISHABLE_KEY` (same)
- `API_BASE_URL` — `http://localhost:8000` (dev)

---

## Open GitHub Issue

**#79** — Pre-flight checklist: what MUST be verified before further server/frontend work.
https://github.com/RizkiRdm/vanguard-ai-jobHunting/issues/79

---

## Recovery References (Local Only)

- `rescue/pre-migration-recovery-2026-10-22` → baseline `4d929e5` (pre-migration Python)
- `v0.1.0-pre-ts-migration` tag → `4d929e5`
- `recovery/pre-migration-state-2026-10-22` tag → `4d929e5`
- `refs/backup/worktree-2026-10-22` → stash of dirty tracked tree
- Untracked tarball: `/tmp/opencode/vanguard-recovery/untracked-2026-10-22.tar.gz`

---

## Next Session: Start Here

1. Read this file + `AGENTS.md` + `docs/SETUP.md`
2. Check GitHub issue #79 for the pre-flight checklist
3. Decide which blocker to tackle first (recommend: rotate secret key + auth E2E)
4. Run `npm run typecheck && npm run lint && npm test` to confirm baseline
5. DO NOT push/deploy without explicit approval

---

## What NOT to Do

- Don't claim anything is deployed or production-ready
- Don't fabricate job listings, employers, or application results
- Don't add Redis, message brokers, second ORMs, or second UI frameworks
- Don't bypass CAPTCHA, MFA, or rate limits on external sites
- Don't expose service-role key, Playwright objects, or `.browser-state/` to client
- Don't put tokens in URLs; session cookies stay HttpOnly
- Don't use `drizzle-kit push` or `drizzle-kit migrate` for schema changes
- Don't edit applied migrations; add new ones