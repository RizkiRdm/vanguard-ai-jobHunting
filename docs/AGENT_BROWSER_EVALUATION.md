# Agent-Browser Evaluation (Issue #87, Phase 1)

Date: 2026-11-14
Scope: **Research + proof of concept only.** No production browser code changed. Phase 2 not started.

## Baseline (current)

- Runtime: Node.js >= 22, Hono API + separate worker, Playwright (Chromium), Gemini.
- Implementation: `apps/server/src/infrastructure/browser/session.ts` (launches Chromium, per-user `storageState` in `.browser-state/<user>.json`, isolated `BrowserContext`, no CDP/debug port), `discovery.ts` (search/scrape with `Page`), `application.ts` (screenshot → AI decision → action loop, approval gate before submit).
- Worker constraints: durable task leases/heartbeats/retries, observable errors, log redaction, **no submit without explicit approval**, no CAPTCHA/MFA/rate-limit bypass, browser state treated as credentials.

## Phase 1 — Research

Tool evaluated: `agent-browser` **0.41.1** (global CLI, `/home/rizki/.nvm/.../bin/agent-browser`). Not a project dependency.

| Area               | Findings                                                                                                                                                                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Interface          | CLI/daemon model (`agent-browser <cmd>`), session-scoped (`--session`). Not an in-process Node API like Playwright `Page`. Programmatic use from worker would require shell/IPC per action and output parsing (text/JSON).                       |
| Browser lifecycle  | Launch on `open`, `close [--all]`; sessions/listing supported. Daemon-backed; cleanup verified with `close`.                                                                                                                                     |
| Page interaction   | `open`, `snapshot` (accessibility tree with refs, `-i` interactive), `click/fill/type/press/scroll`, `get`, `eval`, `screenshot/pdf`, `wait`, network/storage/cookies tabs etc. Ref-based AI flow differs from current screenshot+selector flow. |
| State persistence  | `--state <path>` load, `--restore`/`--profile`/`auth save                                                                                                                                                                                        | login`, cookie/storage commands. Could map to per-user state, but format/credential-handling parity with Playwright `storageState` files not verified.                                          |
| Timeouts/errors    | `wait` supports element/time waits; failure surfaces as command error (exit/non-zero message). In POC, `wait "#missing" 500` reported a longer default timeout than expected — CLI semantics need careful wrapping.                              |
| Security           | No CDP port by default; `connect <port                                                                                                                                                                                                           | url>`and CDP-related commands exist — must not expose debug ports.`--allowed-domains` available. Session isolation by name/namespace; per-user credential isolation must be enforced by caller. |
| Deployment (Linux) | Ran in this environment (browser launched). Requires browser binaries/system deps similar to Chromium automation; operational model (daemon, sockets, `~/.agent-browser` state) differs from in-process Playwright.                              |
| Current coupling   | Worker/browser code is tightly coupled to Playwright types (`Page`, `BrowserContext`) and in-process control (tight AI loop, heartbeats between steps, structured errors).                                                                       |

## Phase 1 — Proof of concept (isolated, harmless)

Commands executed against `file:///tmp/opencode/poc-form.html` (local test form):

- `agent-browser --session poc-eval open file:///tmp/opencode/poc-form.html` → browser launched, page opened.
- `snapshot -i` → interactive elements discovered (heading, 2 textboxes, button with refs).
- `fill "#name"` / `fill "#email"` / `click "#submit"` / `get text "#out"` → `ok` (form interaction succeeded).
- `wait "#does-not-exist" 500` → timed out with error (failure path observed); session remained controllable.
- `close` (twice) → browser closed cleanly.

No live job sites, no CAPTCHA/MFA/rate-limit interaction, no secrets or browser-state exposure.

## Comparison and trade-offs

- **Pros:** rich agent-oriented commands (snapshots/refs), built-in session/restore tooling, broad automation surface.
- **Cons for Vanguard now:** CLI indirection vs embedded `Page` API; would require a new adapter and rework of the screenshot→decision→action loop and per-user state handling; daemon/session lifecycle to operate in the worker; unverified parity for approval-gated submit flow, lease-bound long steps, and credential-safe state storage.
- **Risk:** migration touches safety-critical flow (approval before submit) and durable worker behavior; benefit over current working Playwright is not demonstrated.

## Recommendation: **Defer** (no Phase 2 now)

Adopt/defer/reject: **defer**. Phase 1 shows basic browser actions and cleanup work, but not a clear benefit or parity for Vanguard's worker (per-user state as credentials, approval gate, leases/retries, tight in-process AI loop). Playwright remains the supported implementation.

**If revisited (Phase 2, only on explicit go):** define a narrow browser adapter decoupling task logic from the tool, migrate one workflow behind a feature flag, preserve leases/heartbeats/retries/log redaction and approval-before-submit, keep Playwright for rollback, and remove Playwright only after parity and deployment verification. Do not rewrite AI reasoning loop/API/DB/UI as part of migration.

## Acceptance (Phase 1)

- [x] Research findings and defer decision recorded.
- [x] Reproducible POC demonstrated basic actions and timeout/error cleanup.
- [x] No production code, API contracts, or task lifecycle changed.
- [x] No CAPTCHA/MFA/rate-limit bypass or secret/browser-state exposure.
- [x] Existing implementation not deleted; live-site tests not run (explicitly out of scope for POC).
