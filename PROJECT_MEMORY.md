# Vanguard AI Job Hunting — Project Memory

**Last updated:** 2026-11-20 | **Commit:** `4aaf0e5` (main) | **Branch:** main

---

## Project Overview

Vanguard is an AI job hunting assistant that discovers real job listings, prepares application materials, and fills in application forms in a browser. **Never submits without explicit user approval.**

**Status:** Active Development — Roadmap plan approved (`docs/vanguard-implementation-plan-g-2026-11-18-approved.md`). All 7 roadmap issues (#88, #89, #90, #91, #92, #93, #94) resolved, verified, and closed.

---

## Stack (Locked)

| Layer       | Technology                                                                      |
| ----------- | ------------------------------------------------------------------------------- |
| Frontend    | SvelteKit 3 + Svelte 5 + TypeScript                                             |
| API         | Hono on Node.js 22+                                                             |
| Browser     | Playwright (Chromium)                                                           |
| Database    | Supabase PostgreSQL (Postgres 16)                                               |
| Auth        | Supabase Auth (JWT verification via `@supabase/server` + JWKS)                  |
| Storage     | Supabase Storage (private `resumes` bucket, 10 MB, PDF only)                    |
| Query Layer | Drizzle ORM over `postgres.js` (SQL remains authoritative)                      |
| Migrations  | Plain SQL in `supabase/migrations/` applied via `bun run db:migrate`            |
| AI          | Gemini via Vercel AI SDK (`@ai-sdk/google`) with JSON validation + token budget |
| Contracts   | Zod in `packages/contracts` (shared server/web)                                 |
| Testing     | Vitest (unit), integration tests need `TEST_DATABASE_URL`                       |

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
- ✅ Browser automation (Playwright): per-user contexts, `.browser-state/` (0700/0600), no CDP exposure
- ✅ AI: `generateJson` with Zod validation, token reservation + settlement, budget 429
- ✅ CI workflow updated: Postgres service container + local-stub.sql for integration tests (TEST_DATABASE_URL set)
- ✅ SvelteKit web: login, profile, resume upload, task list/detail, discovery/apply forms, polling
- ✅ Shared contracts (`packages/contracts`)
- ✅ Documentation rewrite (Diátaxis): README, SETUP, ARCHITECTURE, REFERENCE, AUDIT, AGENTS
- ✅ Mobile-first dark UI system (issue #82): docs/DESIGN.md + tokens in app.css, StatusBadge, +error page, dashboard/profile/login/task detail restyled
- ✅ **#84 (2026-11-14, `bcac122`)**: worker startup env loading fixed — `getEnv()` loads cwd + repo-root `.env` (`REPO_ROOT_ENV`) so `bun run worker` boots from root and `apps/server`; regression test in `apps/server/src/config/env.test.ts`.
- ✅ **#85 (2026-11-14, `f832ce4`)**: auth email-confirmation audit — confirmed `public.users` stores no passwords (Supabase Auth owns credentials); actionable sign-in/signup messaging via `apps/web/src/lib/auth{.ts,.test.ts}`; vitest includes web tests; `docs/SETUP.md` clarified (local confirm-email off, prod on).
- ✅ **#86 (2026-11-14, `3a7ed00`)**: local Supabase + cloud promotion workflow defined — `supabase/config.toml`, gitignored local state, `docs/SETUP.md`/`docs/ARCHITECTURE.md` document single `public.schema_migrations` history via `bun run db:migrate` and explicit migration-only promotion (no local data/secrets).
- ✅ **#87 (2026-11-14, `03b9c3e`, Phase 1 defer)**: `agent-browser` evaluated (0.41.1 POC: open/snapshot/fill/click/timeout/cleanup). Findings + **defer** recorded in `docs/AGENT_BROWSER_EVALUATION.md`; Playwright unchanged, Phase 2 requires explicit go.
- ✅ **#88 (2026-11-18, `b6429cd`)**: DuckDuckGo TLS cert navigation error fixed — canonical endpoint `https://duckduckgo.com/html/` with fallback to `https://html.duckduckgo.com/html/`, retry loop, unwrap redirect decoding, and regression unit tests.
- ✅ **#93 (2026-11-19, `6a87dd9`)**: UI standardization with Tailwind CSS v4 & DaisyUI v5 — `PasswordInput.svelte` with show/hide toggle and full ARIA accessibility, DaisyUI forms, cards, alerts, badges across app.
- ✅ **#89 (2026-11-19, `6a87dd9`)**: Routing restructure — public landing page at `/`, authenticated user dashboard moved to `/dashboard`, `PUBLIC_PATHS` updated to permit `/`, `/login`, `/auth/callback`, auth redirects updated.
- ✅ **#90 (2026-11-19, `6a87dd9`)**: Google OAuth + email/password login — "Continue with Google" OAuth trigger, `/auth/callback/+server.ts` code exchange for session cookies with open-redirect protection.
- ✅ **#94 (2026-11-19, `6a87dd9`)**: Public responsive landing page at `/` — built with DaisyUI + Anime.js micro-interactions, responsive mobile/tablet/desktop layouts, strict human-in-the-loop guarantee banner, `prefers-reduced-motion` compliance.
- ✅ **#91 (2026-11-20, `4aaf0e5`)**: Resume upload AI auto-population & dynamic UI states — multimodal Gemini extraction directly from uploaded PDF resume buffer, schema extraction with validation, profile auto-merge preserving existing user data, dynamic upload progress state machine (`idle` -> `uploading` -> `parsing` -> `success`), and mobile-first responsive DaisyUI controls.
- ✅ **#92 (2026-11-20, `4aaf0e5`)**: Human-in-the-loop task notifications & resumption — mobile-first dashboard attention banner with direct "Answer & Resume" and "Review & Approve" actions, task view auto-polling every 3s, responsive interactive HITL card with optimistic submission states and submission payload review.
- ✅ Latest checks (2026-11-20): `bun run check` (typecheck + svelte-check with 0 warnings, lint, format:check, test with 29 passed / 4 DB skipped, and full production build) all pass.
- ✅ Roadmap Plan: `docs/vanguard-implementation-plan-g-2026-11-18-approved.md` completed.
- ✅ Git: `main` at `4aaf0e5`.

---

## Critical Blockers / Unverified

| Area                            | Blocker                                                                                                                                                                         | Resolution Needed                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Credentials**                 | Real `SUPABASE_SECRET_KEY`, DB password, publishable key were in `.env.example` locally (never committed, now placeholders)                                                     | Rotate `SUPABASE_SECRET_KEY` in dashboard                                                    |
| **Wrong project residue**       | Empty `resumes` bucket on `orjicvxvqrvrazazclha` (cannot delete via SQL, `storage.protect_delete`)                                                                              | Delete in that project's dashboard → Storage                                                 |
| **Auth E2E**                    | Only 401 path verified; no real signed-in user token tested. #85 improved messaging/docs but confirm-email toggle not reproduced on a live/local Supabase instance in this env. | Sign up/in via `/login`, call `/tasks` with real token; verify confirm-email on/off behavior |
| **Cross-account isolation**     | Not tested at runtime                                                                                                                                                           | Second account cannot read first's task/resume (expect 404)                                  |
| **Local Supabase verification** | #86 documented workflow/config but Supabase CLI not installed here; `supabase start`/clean rebuild not executed                                                                 | Install CLI, run local stack, build from migrations, verify `public.schema_migrations`       |
| **Cloud promotion**             | Documented as explicit/reviewed; not executed                                                                                                                                   | Apply migrations to hosted project via `DATABASE_URL=<pooler> bun run db:migrate` when ready |
| **DB integration tests**        | 4 tests skipped (need `TEST_DATABASE_URL`)                                                                                                                                      | Run against real DB or decide CI strategy                                                    |
| **Discover task**               | Never run against live DuckDuckGo + Gemini                                                                                                                                      | One end-to-end: queued → running → succeeded                                                 |
| **Apply task**                  | Never run to approval gate                                                                                                                                                      | One end-to-end: stops at `waiting_for_user`, approve re-queues with `submit_selector`        |
| **Token budget**                | 429 path not tested live                                                                                                                                                        | Exceed `DAILY_TOKEN_BUDGET`, confirm 429 + `llm_usage_log` entry                             |
| **Playwright**                  | Chromium launch + `.browser-state/` perms not verified on target                                                                                                                | `node_modules/.bin/playwright install --with-deps chromium`                                  |
| **CI**                          | Never ran on GitHub Actions for current state                                                                                                                                   | Push/confirm typecheck/lint/format/test/build pass                                           |
| **Deployment**                  | No host chosen for long-lived Node + Chromium                                                                                                                                   | Decide before any deploy work                                                                |
| **Repo hygiene**                | Unrelated dirty/untracked files remain; repo-wide `prettier --check .` fails on them                                                                                            | Clean/format or scope format checks in CI intentionally                                      |

---

## Key Architectural Decisions

1. **SQL is authoritative** — `drizzle-kit migrate`/`push` NOT used. RLS, triggers, grants, bucket cannot be expressed in Drizzle schema. Migrations applied via `bun run db:migrate` (idempotent per filename).
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
bun install
cp .env.example .env          # Fill real values (see SETUP.md)
bun run db:migrate            # Apply 6 SQL files (idempotent)
bun run dev:web               # http://localhost:5173
bun run dev:server            # http://localhost:8000
bun run worker                # Background task worker

bun run typecheck             # tsc + svelte-check
bun run lint
bun run test                      # vitest (10 pass, 4 skipped)
bun run build                 # Web production build
bun run format:check
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

## Open GitHub Issues

- **None** — All 7 roadmap issues (#88, #89, #90, #91, #92, #93, #94) are completed, verified, and closed.
- Resolved in this cycle:
  - #88 (`b6429cd`): DuckDuckGo TLS cert fix
  - #93 (`6a87dd9`): UI standardization (Tailwind CSS v4 & DaisyUI v5, PasswordInput, accessibility)
  - #89 (`6a87dd9`): Routing restructure (`/` landing page, `/dashboard` app home, auth guard)
  - #90 (`6a87dd9`): Google OAuth + email/password login flow
  - #94 (`6a87dd9`): Responsive landing page with Anime.js animations
  - #91 (`4aaf0e5`): Resume upload AI autofill & dynamic UI upload states
  - #92 (`4aaf0e5`): Human-in-the-loop task notifications & resumption

---

## Recovery References (Local Only)

- `rescue/pre-migration-recovery-2026-10-22` → baseline `4d929e5` (pre-migration Python)
- `v0.1.0-pre-ts-migration` tag → `4d929e5`
- `recovery/pre-migration-state-2026-10-22` tag → `4d929e5`
- `refs/backup/worktree-2026-10-22` → stash of dirty tracked tree
- Untracked tarball: `/tmp/opencode/vanguard-recovery/untracked-2026-10-22.tar.gz`

---

## Next Session: Start Here

1. Read `PROJECT_MEMORY.md` and `AGENTS.md`.
2. Baseline checks: `bun run check` (expect all green; 29 unit tests pass, 4 DB integration tests skipped without `TEST_DATABASE_URL`).
3. Next steps / roadmap extensions:
   - End-to-end live testing with real credentials (live DuckDuckGo scrape + Gemini live runs, live browser apply flow).
   - Local Supabase setup verification (`supabase start` and clean rebuild against local instance).
   - Token budget 429 live verification.
   - Production deployment strategy for long-lived Node API, worker, and Chromium containers.
4. Commit and verify incrementally.

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
