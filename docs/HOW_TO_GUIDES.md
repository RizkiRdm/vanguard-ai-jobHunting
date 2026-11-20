# How-To Guides: Common Tasks and Recipes in Vanguard

This document contains problem-oriented recipes for solving specific operational, architectural, and development tasks in Vanguard. Each guide addresses a single objective and provides practical steps to accomplish it.

---

## Table of Contents

1. [How to Configure Google OAuth](#1-how-to-configure-google-oauth)
2. [How to Review and Approve Human-in-the-Loop Tasks](#2-how-to-review-and-approve-human-in-the-loop-tasks)
3. [How to Calibrate LLM Token Budgets and Rate Limits](#3-how-to-calibrate-llm-token-budgets-and-rate-limits)
4. [How to Debug Browser Workflows in Headed Mode](#4-how-to-debug-browser-workflows-in-headed-mode)
5. [How to Add and Deploy Database Migrations](#5-how-to-add-and-deploy-database-migrations)
6. [How to Run Integration Tests Against a Local Database](#6-how-to-run-integration-tests-against-a-local-database)

---

## 1. How to Configure Google OAuth

### Goal

Enable users to sign in to Vanguard using their Google credentials via Supabase Auth.

### Steps

1. **Obtain Google Cloud OAuth Credentials**:
   - Go to the [Google Cloud Console](https://console.cloud.google.com/).
   - Navigate to **APIs & Services** > **Credentials**.
   - Create an **OAuth 2.0 Client ID** (Web application).
   - In **Authorized redirect URIs**, add:
     ```
     https://<your-supabase-project-ref>.supabase.co/auth/v1/callback
     ```
   - Copy the **Client ID** and **Client Secret**.

2. **Configure Supabase Auth Provider**:
   - In your [Supabase Dashboard](https://supabase.com/dashboard), navigate to **Authentication** > **Providers** > **Google**.
   - Enable the Google provider.
   - Paste the Google Client ID and Client Secret, then click **Save**.

3. **Verify Vanguard Client Configuration**:
   - Ensure `apps/web/src/routes/auth/callback/+server.ts` is in place.
   - When a user clicks **Continue with Google** on `/login`, Vanguard requests OAuth with `redirectTo: window.location.origin + '/auth/callback'`.
   - The callback exchanges the auth code for a verified Supabase session and sets secure `HttpOnly` cookies.

---

## 2. How to Review and Approve Human-in-the-Loop Tasks

### Goal

Inspect applications paused at the `waiting_for_user` safety gate, answer agent queries, and grant final approval for form submission.

### Steps

1. **Locate Tasks Awaiting Action**:
   - Visit the **Dashboard** (`/dashboard`).
   - If tasks are awaiting your decision, an **Action Required: Pending Applications** amber banner appears with action buttons for each waiting task.

2. **Inspect Form Details**:
   - Click **Review & Approve →** on the dashboard card to open the task details (`/tasks/:taskId`).
   - Scroll to the **Review & Decision Required** card.
   - Inspect the captured submission payload and selector details in the collapsable **Submission payload & selector details** accordion.

3. **Respond to Agent Inquiries**:
   - If the task is awaiting user input (e.g., "What is your desired salary?" or "Are you authorized to work in the US?"), enter your response into the textarea.
   - Click **Submit Answer & Resume**. The worker picks up the answer and continues filling the form.

4. **Authorize Final Submission**:
   - Once all steps are complete and the agent is ready to submit, the card prompts for final authorization.
   - Add an optional review note if desired.
   - Click **Approve & Submit Application**.
   - The task transitions back to `queued` with approval metadata attached; the worker claims it, verifies the approval record, clicks the submit button, and marks the task `succeeded`.

---

## 3. How to Calibrate LLM Token Budgets and Rate Limits

### Goal

Prevent runaway AI costs and protect against API abuse by configuring token spend limits and request throttling.

### Steps

1. **Adjust Daily Token Budget**:
   - In `.env`, modify the `DAILY_TOKEN_BUDGET` variable (defaults to `1,000,000` tokens per user per calendar day):
     ```dotenv
     DAILY_TOKEN_BUDGET=500000
     ```
   - The worker atomically reserves tokens via `reserve_llm_tokens()` before calling Gemini and settles the actual usage via `settle_llm_tokens()`. If a user exceeds their budget, calls return `429 Too Many Requests`.

2. **Adjust Discovery and Apply Rate Limits**:
   - In `.env`, configure the fixed-window limits:
     ```dotenv
     RATE_LIMIT_MAX=20              # Max requests per window
     RATE_LIMIT_WINDOW_SECONDS=60   # Window duration in seconds
     ```
   - The API enforces these limits on `POST /tasks/discover` and `POST /tasks/apply` via `consume_rate_limit()` in Postgres.

---

## 4. How to Debug Browser Workflows in Headed Mode

### Goal

Visually observe Chromium navigating job applications and interacting with web elements for local debugging.

### Steps

1. **Toggle Headless Setting**:
   - In `.env`, change `BROWSER_HEADLESS` to `false`:
     ```dotenv
     BROWSER_HEADLESS=false
     ```

2. **Restart the Worker**:
   - In the terminal running the worker:
     ```bash
     bun run worker
     ```

3. **Launch a Task**:
   - Create an application task from the web UI.
   - A Chromium window will open on your desktop, showing Playwright navigating to the job URL, capturing element screenshots, and filling form inputs in real time.
   - _Note_: Remember to reset `BROWSER_HEADLESS=true` for headless CI or production environments.

---

## 5. How to Add and Deploy Database Migrations

### Goal

Add a new column, SQL function, or table without breaking existing RLS security policies or migration tracking.

### Steps

1. **Create the Migration File**:
   - Add a new `.sql` file in `supabase/migrations/` using timestamp prefix ordering:
     ```
     supabase/migrations/20261120000001_add_feature_table.sql
     ```

2. **Write Migration SQL**:
   - Include the table creation, RLS enablement, and specific grants:
     ```sql
     CREATE TABLE public.custom_data (
       id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
       user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
       content text NOT NULL,
       created_at timestamptz NOT NULL DEFAULT now()
     );

     ALTER TABLE public.custom_data ENABLE ROW LEVEL SECURITY;

     CREATE POLICY "custom_data_owner"
       ON public.custom_data
       FOR ALL
       TO authenticated
       USING (user_id = (SELECT auth.uid()))
       WITH CHECK (user_id = (SELECT auth.uid()));
     ```

3. **Apply the Migration Locally**:

   ```bash
   bun run db:migrate
   ```

   _The runner executes any unapplied SQL files in alphabetical order and logs them to `public.schema_migrations`._

4. **Update Query Types in Drizzle**:
   - Mirror the new table types in `apps/server/src/db/schema.ts` for type safety. _Do not use `drizzle-kit push`_.

---

## 6. How to Run Integration Tests Against a Local Database

### Goal

Run the complete repository test suite including database integration tests (`repository.integration.test.ts`).

### Steps

1. **Prepare Local Postgres**:
   - Start a local Postgres container or instance (e.g., via Docker or Supabase CLI):
     ```bash
     docker run -d --name vanguard-pg -e POSTGRES_PASSWORD=postgres -p 54322:5432 postgres:16
     ```

2. **Apply Local Auth/Storage Stubs**:
   - Run the local stub script to create mock `auth` and `storage` schemas:
     ```bash
     psql postgresql://postgres:postgres@localhost:54322/postgres -f supabase/local-stub.sql
     ```

3. **Run the Test Suite with TEST_DATABASE_URL**:
   ```bash
   TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:54322/postgres" bun run test
   ```
   The integration suite will apply migrations and execute all database assertions rather than skipping them.
