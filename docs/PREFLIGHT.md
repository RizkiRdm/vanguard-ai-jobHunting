# Pre-flight Verification Report (Issue #79)

Generated: 2026-10-25 | Branch: `feat/preflight-79-ai-migration`

## Verified (local)

| # | Item | Evidence |
|---|------|----------|
| 1 | CI env var mismatch fixed | `.github/workflows/ci.yml` updated to `SUPABASE_PUBLISHABLE_KEY`, `SUPABASE_SECRET_KEY`, `SUPABASE_URL`, `SUPABASE_JWKS_URL` |
| 2 | `.env` not tracked | `git ls-files .env` returns empty |
| 3 | `.browser-state/` not tracked | `git ls-files .browser-state` returns empty |
| 4 | No secrets in pushed history | `git log -p -- .env.example \| grep -E 'sb_secret\|sb_publishable'` empty |
| 5 | Node 22+ | v24.18.0 |
| 6 | Typecheck | `npm run typecheck` — 0 errors |
| 7 | Lint | `npm run lint` — 0 warnings |
| 8 | Format | `npm run format:check` — gemini.ts fixed (pre-existing issues in untracked files remain) |
| 9 | Unit tests | `npm test` — 10 passed, 4 skipped (DB tests need TEST_DATABASE_URL) |
| 10 | Web build | `npm run build` — success |
| 11 | Playwright Chromium | Installed (no-op = already present) |
| 12 | AI gateway migrated | `@google/genai` → Vercel AI SDK (`ai` + `@ai-sdk/google`); `generateJson` signature unchanged |

## Not verified — requires human action

| # | Item | Action needed |
|---|------|---------------|
| A | Rotate `SUPABASE_SECRET_KEY` | Supabase dashboard → API keys → rotate |
| B | Delete leftover `resumes` bucket on wrong project `orjicvxvqrvrazazclha` | Dashboard → Storage (SQL blocked by `storage.protect_delete()`) |
| C | Auth E2E (signup/signin, `/tasks`, cross-account isolation) | Browser session + second account |
| D | Discover task end-to-end (live DDG + Gemini) | Worker running + real credentials |
| E | Apply task to approval gate | Worker + real job site |
| F | Token budget 429 path | Live Gemini call exceeding budget |
| G | CI workflow actually running on GitHub | Push/trigger |
| H | Decide TEST_DATABASE_URL in CI vs local-only | User decision |
| I | Decide deployment secrets location | User decision |
| J | DB integration tests (4 skipped) | Skipped — user said no Docker; run locally with `TEST_DATABASE_URL` if needed |

## AI Gateway Migration Summary

- **Before**: `@google/genai` (`GoogleGenAI` client, `generateContent` with JSON response MIME type)
- **After**: Vercel AI SDK (`generateText` + `Output.object({ schema })` from `ai`, `google()` from `@ai-sdk/google`)
- **Unchanged**: `generateJson` signature, token reservation/settlement SQL, `llm_usage_log`, error codes, `AiDecision` schema, `AGENT_SYSTEM_PROMPT`
- **Image input**: now `{ type: 'file', mediaType: 'image/png', data: base64 }` in message content parts
- **Usage extraction**: `result.usage.inputTokens` / `outputTokens` / `totalTokens`

## Decisions needed from user

1. **TEST_DATABASE_URL in CI**: Currently CI skips DB tests silently. Either provide a test DB in CI or accept local-only.
2. **Deployment secrets**: API + worker need a host that allows Chromium. Supabase doesn't run them.
3. **AI model**: Still `gemini-2.0-flash` via Vercel AI SDK. No change needed.

## Next steps

1. Review this PR
2. Complete human-action items A-I
3. Run integration tests locally if desired: `TEST_DATABASE_URL=... npx vitest run`
4. Decide on deployment host before deploy work