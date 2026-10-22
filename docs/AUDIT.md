# Audit of the Python implementation and what replaced it

Scope: the FastAPI/SQLAlchemy implementation that existed before the TypeScript
rewrite (~1,900 lines: `main.py`, `core/`, `modules/`, `shared/`, `UI/`, `tests/`).
Every item below was confirmed by reading the code, then fixed or removed. The
current surface (endpoints, env, SQL functions) is in [REFERENCE.md](REFERENCE.md);
how the pieces fit is in [ARCHITECTURE.md](ARCHITECTURE.md).

## Authentication and authorization

| Finding                                                         | Evidence                                                                      | Resolution                                                                                                                  |
| --------------------------------------------------------------- | ----------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Login endpoint minted a token for any `user_id` query parameter | `modules/agent/agent_router.py` `POST /agent/login`                           | Removed. Supabase Auth is the only identity provider.                                                                       |
| Test login minted a token for `"test-user"` without credentials | `POST /agent/login-test`                                                      | Removed.                                                                                                                    |
| JWT secret had a hardcoded fallback                             | `core/security.py` `os.getenv("JWT_SECRET_KEY", "vanguard_ultra_secret_key")` | No app-issued JWTs remain. Server verifies Supabase tokens against the project JWKS (`verifyAuth` from `@supabase/server`). |
| Unauthenticated debug endpoint reset the rate limiter           | `main.py` `POST /test/reset-rate-limit`                                       | Removed. Rate limits are SQL-backed.                                                                                        |
| Browser sent the access token in a WebSocket query string       | `UI/index.html` `?token=`                                                     | Removed. No tokens in URLs.                                                                                                 |
| UI read an HttpOnly cookie from JavaScript                      | `UI/index.html` `document.cookie`                                             | Removed. Session is read on the SvelteKit server only.                                                                      |
| No ownership checks on task/profile resources                   | routers filtered by id only                                                   | Every repository query filters on the authenticated `user_id`; RLS policies mirror it.                                      |

## Data integrity and durability

| Finding                                                                             | Evidence                                                   | Resolution                                                                                                               |
| ----------------------------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Job scraper returned hardcoded fictional listings and saved them                    | `core/scraper.py` `Example Corp`, `example.com/jobs/1`     | Replaced by real DuckDuckGo result scraping. Nothing is invented.                                                        |
| Worker marked every finished task `COMPLETED`, including tasks waiting for the user | `core/worker.py` `update_task_status(..., COMPLETED)`      | Tasks finish or park through SQL functions that check worker and status.                                                 |
| Claimed tasks had no lease; a crashed worker left them `RUNNING` forever            | `core/task_manager.py` `claim_next_task`                   | `claim_task` sets a lease, workers heartbeat, `reclaim_expired_tasks` requeues.                                          |
| Inbound HITL answers were read but never handled                                    | `agent_router.py` `await websocket.receive_text()`         | `resume_task` merges the answer into the payload and requeues.                                                           |
| AI could submit an application with no user confirmation                            | `orchestrator._dispatch_action`, `prompts/agent_prompt.md` | Agent stops at `ready_to_submit`; submission requires an approve action.                                                 |
| Token budget was check-then-insert, so concurrent requests overspent                | `core/ai_agent.py` `check_budget_limit`                    | `reserve_llm_tokens` is a single conditional UPDATE; tokens settle afterwards.                                           |
| Initial Alembic migration was empty                                                 | `migrations/versions/1b8f418aab69` `upgrade(): pass`       | Versioned SQL migrations in `supabase/migrations`, applied by `npm run db:migrate`.                                      |
| Enum/type mismatch (`APPLYING` vs `AUTOMATED_APPLY`), `uuid.UUID()` on non-UUID ids | `core/orchestrator.py`                                     | Typed task `type`/`status` in shared contracts, CHECK constraints in SQL.                                                |
| Encryption key was regenerated per process when unset                               | `core/security.py` `Fernet.generate_key()`                 | Nothing is encrypted with a throwaway key. Site credentials are not stored; expired sessions park the task for the user. |

## Files and logs

| Finding                                                     | Evidence                               | Resolution                                                                                                                              |
| ----------------------------------------------------------- | -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| Upload validation trusted the client MIME type, no size cap | `modules/profile/profile_router.py`    | 10 MB cap, `application/pdf` check, `%PDF-` magic-byte check, server-generated object name.                                             |
| Files stored under predictable local paths                  | `storage/resumes/{user_id}_resume.pdf` | Private Supabase bucket, `${userId}/${uuid}.pdf`, 60 s signed URLs only.                                                                |
| VirusTotal scanner existed but was never called             | `core/security.py` `MalwareScanner`    | Removed. The scanner was unreachable dead code; format and size checks remain.                                                          |
| SQL echo logging was on                                     | `core/database.py` `echo=True`         | Drizzle over `postgres.js` with `onnotice` suppressed; structured logger redacts secrets, tokens, cookies, CV and cover-letter content. |
| Browser session state kept indefinitely on disk             | `storage/sessions/auth_*.json`         | Per-user state in `.browser-state/` with 0700/0600 permissions, never served over HTTP. Removed the legacy files.                       |

## Hardening found while standing up Supabase

These are not legacy defects; they are Supabase defaults that would have left the
new schema weaker than intended. They were first reproduced on a local Postgres 16
with the stubs in `supabase/local-stub.sql`, and the fixes are present in the
migrations now applied to the hosted project.

| Finding                                                                       | Why it matters                                                                                                                            | Resolution                                                                                                                                        |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Supabase grants EXECUTE on new public functions to `anon` and `authenticated` | `reserve_llm_tokens(p_user => …)` would let an anonymous caller spend another user's budget; `claim_task` would let them compete for work | `20260101000003_function_grants.sql` and `20260101000004_hardening.sql` revoke from `public`, `anon` and `authenticated`, grant to `service_role` |
| Function `search_path` was mutable                                            | A caller-controlled schema could shadow objects referenced inside a function                                                              | `search_path = ''` pinned on all 13 functions                                                                                                     |
| RLS policies were declared without a role and used `auth.uid()` inline        | Policies applied to `anon` too, and the check ran per row                                                                                 | Policies now use `to authenticated` with `(select auth.uid())`, and `using` plus `with check`                                                     |
| `rate_limits` had RLS disabled                                                | Any role with table access could read or reset other keys                                                                                 | RLS enabled with a `service_role`-only policy                                                                                                     |
| `handle_new_auth_user()` is `SECURITY DEFINER` in `public`                    | Public functions are callable by default                                                                                                  | EXECUTE revoked from `anon`, `authenticated` and `public`                                                                                         |

## Removed dead code

`MalwareScanner`, `GoogleAuthService`, `bcrypt` password helpers, JWT creation
helpers, credential encrypt/decrypt, the MCP→Playwright bridge (`MCPBrowser`,
`BrowserManager`), `cli.py` (it called the insecure login), `UI/index.html`
(replaced by SvelteKit), `config/jobsites.yaml` (selectors now live in the
browser modules), and the Python test suite that required a live Postgres.

## Verification performed

| Check                            | Command                                                                                                                                                  | Result                                                                                                                                              |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Type checks                      | `npm run typecheck`                                                                                                                                      | `tsc` clean, `svelte-check` 0 errors 0 warnings                                                                                                     |
| Lint / format                    | `npm run lint`, `npm run format:check`                                                                                                                   | clean                                                                                                                                               |
| Unit tests                       | `npm test`                                                                                                                                               | 10 passed (env validation, log redaction, AI response schema)                                                                                       |
| Migrations on a real Postgres 16 | `npm run db:migrate` against a local container with `supabase/local-stub.sql`                                                                            | all 6 files applied, no errors                                                                                                                      |
| Grants and policy shape          | `has_function_privilege('anon', …)`, `pg_policies`                                                                                                       | `anon` cannot execute any internal function, `service_role` can; policies are `to authenticated` with `with check`                                  |
| Migrations on the hosted project | `npm run db:migrate` through the Supavisor pooler (`:6543`), then SQL checks via `pg_tables`, `pg_policies`, `has_function_privilege`, `storage.buckets` | 6 migrations applied; 8 tables with RLS on; `anon` cannot execute internal functions, `service_role` can; `resumes` bucket private, PDF-only, 10 MB |
| Security advisors                | Supabase linter against the hosted project                                                                                                               | was checked while the schema was applied to an earlier project, then reverted with it; not re-run on the current project (the MCP is not used)      |
| SQL functions                    | `claim_task`, `finish_task`, `request_approval`/`approve_task`, `reclaim_expired_tasks`, `reserve_llm_tokens`, `consume_rate_limit`, RLS                 | exclusive claim, lease-owner guard, approval merge, requeue/fail, budget cap, rate window, per-user isolation all held                              |
| Repository integration           | `TEST_DATABASE_URL=... npx vitest run apps/server/src/modules/tasks/repository.integration.test.ts`                                                      | 4 passed                                                                                                                                            |
| API smoke                        | `createApp().fetch` for `/health`, `/ready`, `/tasks`, unknown path, CORS                                                                                | expected status codes and no wildcard origin                                                                                                        |
| Web production build             | `npm run build`                                                                                                                                          | adapter-node build completed                                                                                                                        |

One SQL bug was found this way: the nested `$$` in `20260101000000_init.sql` closed
the outer `DO` block early, so the migration failed until the inner function body
used a distinct tag (`$fn$`).

## Not claimed

No deployment was performed. Browser workflows against live job sites were not
executed in this environment, so no real application submission is recorded. The
approval gate is verified at the SQL and unit level only: the agent stops at
`ready_to_submit`, the task parks, and only an approve action re-queues it.
