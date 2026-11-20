# Tutorial: Your First Automated Job Search and Application with Vanguard

Welcome to Vanguard! This tutorial is a step-by-step, hands-on lesson designed to guide you from a blank terminal to running your first automated job discovery, uploading your resume for AI auto-population, and safely stepping through a human-in-the-loop application workflow.

By the end of this lesson, you will understand how Vanguard's three processes collaborate, how tasks are queued and processed, and how the approval gate guarantees that the AI never submits an application without your explicit permission.

---

## What You Will Learn

1. How to configure and start the Vanguard stack (Web UI, API server, background Worker).
2. How authentication and session management work with Supabase Auth.
3. How resume uploads trigger Gemini AI to extract and populate candidate details.
4. How to launch a DuckDuckGo-powered job discovery task and inspect found listings.
5. How an application task navigates in Playwright and parks at the `waiting_for_user` gate for your review.
6. How to approve or provide feedback to resume the task.

---

## Prerequisites

Before starting, ensure you have:

- **Node.js**: version 22 or higher (`node -v`)
- **Bun**: version 1.2+ (`bun -v`)
- **Supabase Project**: either a free cloud project at [supabase.com](https://supabase.com) or a local Supabase CLI instance.
- **Google Gemini API Key**: from [Google AI Studio](https://aistudio.google.com/).

---

## Step 1: Configure Environment Variables

Vanguard requires configuration for its database, authentication, storage, and AI engine.

1. Copy the example configuration to `.env`:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and fill in your credentials:

   ```dotenv
   # Database: Use your Supavisor transaction pooler URL (port 6543)
   DATABASE_URL="postgresql://postgres.<project-ref>:<password>@aws-0-<region>.pooler.supabase.com:6543/postgres"

   # Supabase: Project URL and keys
   SUPABASE_URL="https://<project-ref>.supabase.co"
   SUPABASE_PUBLISHABLE_KEY="sb_publishable_..."
   SUPABASE_SECRET_KEY="sb_secret_..."
   SUPABASE_JWKS_URL="https://<project-ref>.supabase.co/auth/v1/.well-known/jwks.json"

   # AI: Google Gemini key
   GEMINI_API_KEY="AIzaSy..."
   ```

3. Run the doctor diagnostic to verify that your environment names and dependencies are in order:
   ```bash
   bun run doctor
   ```
   All checks should pass.

---

## Step 2: Initialize Database and Storage

Vanguard uses native SQL migrations to configure tables, triggers, RLS policies, and private storage buckets.

Run the migration script:

```bash
bun run db:migrate
```

You should see each SQL migration file in `supabase/migrations/` applied and logged to `public.schema_migrations`. This sets up:

- The `tasks` queue and worker lease functions (`claim_task`, `finish_task`).
- The `user_profiles` table.
- The `jobs` table for discovered listings.
- The private `resumes` bucket with strict owner-only RLS policies.

---

## Step 3: Start the Vanguard Processes

Vanguard separates the web client, API, and worker into three independent processes so browser automation never blocks user requests.

Open three separate terminal windows:

### Terminal 1: Web Interface (SvelteKit)

```bash
bun run dev:web
```

_Runs at `http://localhost:5173`._

### Terminal 2: API Server (Hono)

```bash
bun run dev:server
```

_Runs at `http://localhost:8000`._

### Terminal 3: Background Worker (Playwright + Gemini)

```bash
bun run worker
```

_Polls for queued tasks, manages browser sessions, and executes LLM reasoning._

---

## Step 4: Sign In to Vanguard

1. Navigate to `http://localhost:5173` in your browser.
2. You will be greeted by the Vanguard landing page.
3. Click **Get Started** or navigate to `http://localhost:5173/login`.
4. Enter your email and password to create an account (or click **Continue with Google** if OAuth is configured).
5. Once authenticated, SvelteKit establishes an `HttpOnly` cookie session and routes you to the **Dashboard** (`/dashboard`).

---

## Step 5: Upload Your Resume for AI Auto-Population

1. Click on **Profile** in the navigation bar (`/profile`).
2. In the **Upload Resume** card, select a PDF file of your resume (under 10 MB).
3. Click **Upload & Extract with AI**.
4. Observe the dynamic state machine:
   - **Uploading**: The PDF buffer is securely transferred to the private Supabase Storage bucket.
   - **AI Extracting**: Gemini's multimodal parser analyzes the PDF structure directly and extracts your contact details, target role, skills, and summary.
   - **Success**: An alert confirms the extracted fields, and your form fields below are automatically pre-populated with your information.
5. Review the extracted fields, tweak any values as desired, and click **Save Profile**.

---

## Step 6: Launch a Job Discovery Task

1. Return to the **Dashboard** (`/dashboard`).
2. Locate the **Discover Jobs** form.
3. Enter a search query (e.g., `Senior TypeScript Engineer remote`) and set the max results to `5`.
4. Click **Start Discovery**.
5. Observe the task card appear under **Recent Tasks** with a `queued` status.
6. Check **Terminal 3 (Worker)**:
   - The worker atomically claims the task using `claim_task()`.
   - The worker performs a DuckDuckGo search without fabricating any data.
   - Extracted listings are stored in the `jobs` table.
7. Click on the task in your dashboard to view the **Task Detail** page (`/tasks/:id`).
8. Notice the live auto-polling (every 3 seconds) updating the status to `succeeded` and displaying the discovered job cards with links and companies.

---

## Step 7: Run an Application and Inspect the Approval Gate

Now experience Vanguard's core safety guarantee: **the human-in-the-loop gate**.

1. On the Task Detail page of your completed discovery, find a job listing and click **Apply via Vanguard**, or return to the Dashboard and submit an **Apply to Job** request with a direct job posting URL.
2. The task starts in `queued` and moves to `running`.
3. In **Terminal 3**, the worker:
   - Launches a headless Chromium browser with an isolated per-user browser profile.
   - Navigates to the application URL.
   - Takes screenshots and asks Gemini to identify form fields and map them to your profile and resume.
   - Fills in form inputs step-by-step.
   - Detects the final submit button.
4. **The Gate Activates**: Instead of clicking submit, the worker executes `request_approval` and parks the task in `waiting_for_user`.
5. On the **Dashboard**, a prominent amber alert banner notifies you that a task requires your attention.

---

## Step 8: Review and Approve the Application

1. Click **Review & Approve →** on the dashboard alert, or visit the task detail page (`/tasks/:id`).
2. The task detail page presents a dedicated **Review & Decision Required** card:
   - You can inspect the submission details and selector captured by the worker.
   - You can review any questions asked by the agent.
3. If an input question is requested:
   - Type your answer in the text field and click **Submit Answer & Resume**. The worker picks up the response and continues.
4. When the form is ready for submission:
   - Enter an optional note (e.g., `Verified salary and contact info`).
   - Click **Approve & Submit Application**.
5. The button transitions with an optimistic loading state (`Submitting approval...`).
6. The worker receives the approved signal, securely executes the final submit click, and updates the task status to `succeeded`.

---

## Next Steps

Congratulations! You have completed a full end-to-end cycle with Vanguard:

- You verified your local configuration with `bun run doctor`.
- You initialized the database schema with `bun run db:migrate`.
- You ran the web UI, API, and background worker in concert.
- You experienced resume AI parsing and the human-in-the-loop approval gate.

To explore further:

- Read [docs/HOW_TO_GUIDES.md](HOW_TO_GUIDES.md) to learn how to configure OAuth, token budgets, and rate limits.
- Consult [docs/ARCHITECTURE.md](ARCHITECTURE.md) for deep dives into queue concurrency and security isolation.
- Check [docs/REFERENCE.md](REFERENCE.md) for complete API, SQL function, and contract specifications.
