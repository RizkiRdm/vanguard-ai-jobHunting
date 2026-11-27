# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Job seekers applying to many roles. They are actively running a high-volume job
hunt and want the repetitive form-filling work automated without losing control
of what is sent to employers.

## Product Purpose

Vanguard discovers real job listings from live web search, extracts structured
profile data from the user's resume, fills application forms in a real browser,
and stops at the finish line. The user inspects what was filled and approves each
submission individually. Success means less time on repetitive application work
and zero unchecked applications sent.

## Positioning

An autonomous application agent with a hard human-in-the-loop gate: it never
clicks submit without an explicit approval recorded for that task. Discovery is
grounded in listings actually seen (an empty result stays empty), and every task
is durable and resumable in Postgres. A conventional auto-apply tool that
submits on its own could not truthfully make that claim.

## Operating Context

The user creates an account, fills in a profile, uploads a PDF resume, and starts
a discovery task from the dashboard. While a task runs, its detail page polls for
status; a task that reaches `waiting_for_user` shows the pending step, and only a
user action re-queues submission. Under the hood a separate worker leases tasks
from Postgres, drives Playwright with per-user browser state, and runs Gemini with
a token budget. Developers run the API, worker and web app as separate local
processes.

Current state: MVP, not deployed. Schema, RLS policies and the private storage
bucket are applied to one hosted Supabase project; API, worker and web app run
locally. No browser workflow has been exercised against a live job site yet.

## Capabilities and Constraints

- Discovery searches DuckDuckGo HTML results; it is a scrape, so selectors can
  change. It stores only listings actually seen.
- Resume PDFs are checked by size, MIME type and `%PDF-` magic bytes, stored in a
  private bucket under server-generated names, and served via short-lived signed
  URLs.
- Gemini responses are JSON-validated and metered by a token budget. Page content,
  job descriptions and AI output are untrusted input.
- Task states are `queued`, `running`, `waiting_for_user`, `succeeded`, `failed`,
  `cancelled`; every transition goes through a SQL function. Claiming uses
  `SELECT … FOR UPDATE SKIP LOCKED`.
- Identity comes only from a verified Supabase access token. Every user-owned
  read and write filters on the authenticated user id; RLS is a backstop, not
  authorization.
- No CAPTCHA, MFA or rate-limit bypass on external sites; the task pauses and
  asks the user instead.
- Postgres is the queue. No Redis, message broker, second ORM or second UI
  framework.
- No real application submissions or outcomes have been observed yet; deployment
  target and hosting are undecided.

## Brand Commitments

Name: Vanguard. No brand assets, logo, or voice constraints were confirmed as
binding by the user. Existing landing-page copy is evidence of current voice,
not a durable commitment.

## Evidence on Hand

README.md, docs/FEATURES.md (feature map), docs/ARCHITECTURE.md, docs/AUDIT.md,
DESIGN.md, the SvelteKit routes and their copy under `apps/web/src/routes`, and
`docs/SETUP.md`. The terminal transcript in the landing page is illustrative UI
copy, not a recorded task result. Absent: live job-site runs, real application
results, customer testimonials, benchmarks, pricing, and a hosted deployment —
future work must not fabricate them.

## Product Principles

1. Approval is mandatory: no application is submitted without a recorded user
   approval for that task.
2. Honest data: never fabricate listings, employers, salaries, statuses or
   results; empty states stay empty.
3. Durable by construction: atomic SQL transitions and leased queue tasks, so
   work is neither dropped nor duplicated after a crash.
4. Least privilege: verified identity on every request, private file storage,
   no secret or browser-state exposure to the client.
5. Untrusted by default: external page content and AI output cannot change agent
   rules or trigger unrelated actions.
