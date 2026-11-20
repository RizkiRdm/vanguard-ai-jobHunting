# Vanguard Implementation Plan: GitHub Issues #88 to #94

Prioritized roadmap for resolving all 7 open repository issues. Execution grouped by dependencies and severity for low-effort execution.

---

## Dependency Graph & Execution Order

```
[Phase 1] #88 (DDG TLS Bug) [Independent Backend Fix]
     │
[Phase 2] #93 (DaisyUI Foundation) ──► #89 (Routing: / vs /dashboard)
     │                                      │
     ├──► [Phase 3] #90 (Google OAuth)     │
     │                                      ▼
     └──► [Phase 4] #94 (Public Landing Page at /)
     │
[Phase 5] #91 (Resume Upload & AI Profile Autofill)
     │
[Phase 6] #92 (Task Resumption & Waiting-for-User Alerts)
```

---

## Phase 1: Critical Bug Fix (Backend / Worker)

### Issue #88: DuckDuckGo navigation ERR_CERT_COMMON_NAME_INVALID in discovery

- **Severity**: High (blocks automated job discovery worker tasks)
- **Problem**: `apps/server/src/infrastructure/browser/discovery.ts` uses hardcoded `https://html.duckduckgo.com/html/` with query params. Fails TLS cert check in certain network environments.
- **Root Cause**: `html.duckduckgo.com` subdomain cert mismatches or TLS termination differences.
- **Proposed Fix**:
  1. Update target URL in `discovery.ts` to canonical `https://duckduckgo.com/html/` or `https://lite.duckduckgo.com/lite/`.
  2. Implement endpoint fallback in `searchJobs()` (try primary endpoint, catch navigation error, retry with fallback).
  3. Keep strict TLS verification intact (`ignoreHTTPSErrors: false` per security rules).
  4. Ensure query parameter encoding handles empty/special characters cleanly.
- **Dependencies**: None.
- **Verification**:
  - Run unit/integration test: `bun run --filter @vanguard/server test`
  - Test discovery handler against live or mocked duckduckgo response without TLS errors.

---

## Phase 2: UI Foundation & Routing Restructure

### Issue #93: Standardize UI with DaisyUI and Tailwind CSS

- **Severity**: Medium (blocks consistent UI for #89, #90, #94, #91, #92)
- **Problem**: Inconsistent ad-hoc styling across web app forms and buttons; missing password visibility toggles and ARIA accessibility standards.
- **Proposed Fix**:
  1. Verify `daisyui` plugin in `apps/web/package.json` and `tailwind.config.js`.
  2. Create reusable form components in `apps/web/src/lib/components/ui/`:
     - Accessible text input with `<label>`, `aria-invalid`, `aria-describedby`, error state.
     - Password input with show/hide toggle button (accessible SVG icon + `aria-pressed`).
     - Standard button states (`btn btn-primary`, `loading`, disabled).
  3. Replace existing raw Tailwind classes across login, register, and profile pages with standardized DaisyUI classes.
- **Dependencies**: None.
- **Verification**:
  - Run `bun run --filter @vanguard/web check`
  - Visual check of login/register/profile forms in browser with keyboard navigation and screen-reader tags.

### Issue #89: Add a Landing Page and Restructure Routing

- **Severity**: Medium (blocks landing page #94)
- **Problem**: `apps/web/src/hooks.server.ts` currently restricts root `/` to authenticated users (`PUBLIC_PATHS = new Set(['/login'])`). Root `/` renders the authenticated dashboard, leaving no space for a public landing page.
- **Proposed Fix**:
  1. Update `PUBLIC_PATHS` in `apps/web/src/hooks.server.ts` to include `'/'` and `'/auth/callback'`.
  2. Move dashboard page from `apps/web/src/routes/+page.svelte` and `+page.server.ts` to `apps/web/src/routes/dashboard/+page.svelte` and `+page.server.ts`.
  3. In `hooks.server.ts`: If authenticated user hits `/`, redirect to `/dashboard`. If unauthenticated hits `/dashboard` or protected routes, redirect to `/login`.
  4. Update navigation links (navbar, login redirects) to point to `/dashboard`.
- **Dependencies**: #93.
- **Verification**:
  - Unauthenticated GET `/` returns 200 (landing stub/page).
  - Unauthenticated GET `/dashboard` redirects 303 to `/login`.
  - Authenticated GET `/` redirects 303 to `/dashboard`.
  - Authenticated GET `/dashboard` loads user jobs and tasks.

---

## Phase 3: Authentication Enhancements

### Issue #90: Google OAuth and Email/Password Login

- **Severity**: Medium
- **Problem**: Login page only supports email/password; lacks Google OAuth provider integration, standard callback handler, and OAuth error feedback.
- **Proposed Fix**:
  1. Add "Continue with Google" button to `apps/web/src/routes/login/+page.svelte` following Google brand guidelines and DaisyUI styling.
  2. Client-side trigger: `supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo: `${window.location.origin}/auth/callback` } })`.
  3. Create route `apps/web/src/routes/auth/callback/+server.ts`:
     - Extract `code` from query params.
     - Exchange code via `supabase.auth.exchangeCodeForSession(code)`.
     - Set session cookies and redirect to `/dashboard` (or return error to `/login?error=...`).
  4. Ensure both email/password form and OAuth handle loading and error states cleanly.
- **Dependencies**: #93 (UI styling), #89 (`/auth/callback` public path).
- **Verification**:
  - Test `/auth/callback` with invalid/missing code → redirects to `/login` with friendly error message.
  - Test login form submission validation and loading spinner.

---

## Phase 4: Public Landing Page

### Issue #94: Responsive Landing Page at `/`

- **Severity**: Low / Enhancement
- **Problem**: Root path needs a responsive, public-facing landing page showcasing Vanguard's AI job-hunting features.
- **Proposed Fix**:
  1. Implement `apps/web/src/routes/+page.svelte` using DaisyUI components:
     - Hero section with clear value proposition and CTA buttons ("Get Started" -> `/login`, "Sign In" -> `/login`).
     - Features grid: Automated Discovery, AI Tailoring, Human-in-the-Loop Browser Automation.
     - How It Works sequence / timeline.
     - Security & privacy guarantee section (never submits without explicit user approval).
  2. Integrate lightweight animations:
     - Use CSS transitions / Anime.js for micro-interactions on button hover, card entrance, and badge pulses.
     - Respect `prefers-reduced-motion` media queries.
  3. Ensure fully responsive layout across mobile, tablet, and desktop breakpoints.
- **Dependencies**: #89 (route available), #93 (DaisyUI tokens).
- **Verification**:
  - Run `bun run --filter @vanguard/web check`
  - Verify layout responsiveness across 320px, 768px, and 1280px viewports.
  - Verify zero console errors or broken navigation links.

---

## Phase 5: Profile & Resume AI Processing [COMPLETED]

### Issue #91: Auto-populate profile fields from uploaded resumes

- **Status**: Completed in commit for Issue #91
- **Severity**: Medium
- **Problem**: Uploading a PDF resume stores the file in Supabase Storage but does not parse text or populate the user profile fields.
- **Implemented**:
  1. Multimodal native PDF extraction in `gemini.ts` using `ResumeProfileExtraction` schema.
  2. Auto-merge of extracted non-empty fields in profile repository.
  3. Dynamic upload state machine (`idle` -> `uploading` -> `parsing` -> `success`) and mobile-first DaisyUI controls in `profile/+page.svelte`.

---

## Phase 6: Human-in-the-Loop Task Alerts & Resumption [COMPLETED]

### Issue #92: Human-in-the-loop task resumption & notifications

- **Status**: Completed in commit for Issue #92
- **Severity**: Medium
- **Problem**: Tasks pausing in `waiting_for_user` (e.g. CAPTCHA, 2FA, approval before submission) have no clear real-time alert or inline resumption UI on the dashboard.
- **Implemented**:
  1. Prominent mobile-first DaisyUI alert banner with actionable CTA buttons on `/dashboard`.
  2. Dedicated interactive HITL card on `/tasks/[id]` with auto-polling every 3s, responsive form with optimistic submission state.

---

## Overall Test & CI Verification Gate

Run before finalizing each phase:

```bash
bun run check        # typecheck + svelte-check + lint + format:check + test + build
bun run test         # all unit tests across contracts, server, and web
```
