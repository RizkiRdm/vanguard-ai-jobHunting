# Vanguard Frontend — Implementation Plan

> **Agent Model:** Gemini Flash-lite / Claude Haiku-equivalent
> **Execution Rules for Agent:**
>
> - Each issue is ONE atomic task. Never combine.
> - Read `DESIGN.md` before starting any issue.
> - Output must match the component spec exactly — no improvisation on colors, fonts, or layout.
> - After completing each issue, commit with `feat(frontend): <issue title>` (Conventional Commits).
> - Do NOT touch any file in `backend/` or project root configs unless the issue explicitly says so.

---

## Phase 0 — Project Bootstrap

### Issue 1: Initialize Vite + React + TypeScript project

```bash
gh issue create \
  --title "feat: initialize vite react typescript project" \
  --body "## Task
Bootstrap the frontend project using Vite with React and TypeScript template.

## Steps
1. Run: \`npm create vite@latest frontend -- --template react-ts\`
2. cd into \`frontend/\`
3. Install dependencies: \`npm install\`
4. Install Tailwind CSS v4: \`npm install -D tailwindcss postcss autoprefixer\`
5. Run: \`npx tailwindcss init -p\`
6. Install additional deps: \`npm install axios lucide-react react-router-dom\`
7. Verify dev server runs: \`npm run dev\`

## Acceptance Criteria
- \`frontend/\` directory exists with working Vite dev server
- No TypeScript errors on fresh start
- Tailwind installed and config files present" \
  --label "phase:0,type:setup"
```

---

### Issue 2: Configure Tailwind with Vanguard design tokens

```bash
gh issue create \
  --title "feat: configure tailwind v4 with vanguard design tokens" \
  --body "## Task
Set up Vanguard design tokens using Tailwind v4 CSS-first configuration.

## Steps
1. Open \`src/index.css\`
2. Add at the top:
\`\`\`css
@import 'tailwindcss';

@theme {
  --color-background: #0A0A0F;
  --color-surface: #111118;
  --color-elevated: #1A1A24;
  --color-border: #2A2A38;
  --color-accent: #6366F1;
  --color-accent-hover: #4F46E5;
  --color-accent-muted: #6366F114;
  --color-text-primary: #F1F1F5;
  --color-text-secondary: #9090A8;
  --color-text-muted: #5A5A72;
  --color-status-running: #22C55E;
  --color-status-awaiting: #F59E0B;
  --color-status-failed: #EF4444;

  --font-sans: 'DM Sans', sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}
\`\`\`
3. Open \`index.html\`, add Google Fonts in \`<head>\`:
\`\`\`html
<link href=\"https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap\" rel=\"stylesheet\">
\`\`\`
4. Verify custom classes work: \`bg-surface\`, \`text-accent\`, \`border-border\`

## Acceptance Criteria
- No \`tailwind.config.js\` created
- All color tokens accessible as Tailwind utility classes
- Both fonts load correctly in browser" \
  --label "phase:0,type:setup"
```

---

### Issue 3: Create TypeScript types and API client

```bash
gh issue create \
  --title "feat: create typescript types and axios api client" \
  --body "## Task
Define all shared TypeScript types and a configured Axios instance.

## Steps

### 1. Create \`src/types/index.ts\`
Define these types exactly:
\`\`\`ts
export type TaskStatus = 'QUEUED' | 'RUNNING' | 'AWAITING_USER' | 'COMPLETED' | 'FAILED';
export type TaskType = 'DISCOVERY' | 'APPLY';

export interface AgentTask {
  id: string;
  type: TaskType;
  status: TaskStatus;
  created_at: string;
  metadata: {
    thought?: string;
    action?: string;
    subjective_question?: string;
    human_answer?: string;
    logs?: Array<{ type: 'THOUGHT' | 'ACTION' | 'OBSERVE' | 'ERROR'; message: string; ts: string }>;
  };
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  resume_filename?: string;
  stats: {
    total_applied: number;
    total_discovered: number;
    token_cost: number;
  };
}
\`\`\`

### 2. Create \`src/api/index.ts\`
\`\`\`ts
import axios from 'axios';
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000', withCredentials: true });
export default api;
\`\`\`

### 3. Create \`src/api/profile.ts\`
Functions: \`getProfile()\` → GET /profile/me, \`updateProfile(data)\` → PUT /profile/me, \`uploadResume(file)\` → POST /profile/resume (multipart)

### 4. Create \`src/api/agent.ts\`
Functions: \`getTasks()\` → GET /agent/tasks, \`stopTask(id)\` → POST /agent/tasks/{id}/stop, \`sendAnswer(id, answer)\` → POST /agent/interact/{id}, \`getScreenshot(id)\` → GET /agent/tasks/{id}/screenshot, \`startScrape(url)\` → POST /agent/scrape

## Acceptance Criteria
- No TypeScript errors
- All API functions exported correctly" \
  --label "phase:0,type:setup"
```

---

## Phase 1 — Layout & Navigation

### Issue 4: Build AppShell layout with Sidebar

```bash
gh issue create \
  --title "feat: build appshell layout with sidebar" \
  --body "## Task
Create the main app layout: fixed sidebar on left, scrollable main content on right.

## Reference
See DESIGN.md — Section 4 (Layout) and Section 5.1 (Sidebar).

## Steps

### 1. Create \`src/components/layout/Sidebar.tsx\`
- Width: \`w-56\` fixed
- Background: \`bg-background-surface border-r border-background-border\`
- Top: Logo area \`h-16\` with text 'Vanguard' + Shield icon from lucide-react
- Nav items (icon + label):
  - Dashboard → path \`/\` → LayoutDashboard icon
  - Jobs → path \`/jobs\` → Briefcase icon
  - Profile → path \`/profile\` → User icon
  - Settings → path \`/settings\` → Settings icon
- Active state: \`bg-accent/10 text-accent\`
- Inactive state: \`text-text-secondary hover:bg-background-elevated hover:text-text-primary\`
- Use \`NavLink\` from react-router-dom for active detection
- Bottom: Agent status badge (hardcoded 'Agent Idle' for now with gray dot)

### 2. Create \`src/components/layout/AppShell.tsx\`
- \`flex h-screen\` root
- \`<Sidebar />\` + \`<main className='flex-1 overflow-y-auto'>\`

### 3. Update \`src/App.tsx\`
- Wrap routes in \`<AppShell />\`
- Add \`BrowserRouter\` + routes for \`/\`, \`/jobs\`, \`/profile\`, \`/settings\`
- Each route renders a placeholder \`<div>Page name</div>\` for now

## Acceptance Criteria
- Sidebar visible and fixed on all routes
- NavLink active styles apply correctly
- Main content scrolls independently" \
  --label "phase:1,type:feature"
```

---

## Phase 2 — UI Primitives

### Issue 5: Build Button primitive component

```bash
gh issue create \
  --title "feat: build button primitive component" \
  --body "## Task
Create a reusable Button component with 3 variants per DESIGN.md Section 5.6.

## Steps
Create \`src/components/ui/Button.tsx\`:
\`\`\`tsx
// Props: variant ('primary' | 'ghost' | 'danger'), size ('sm' | 'md'), disabled, onClick, children, className
// variant='primary'  → bg-accent hover:bg-accent-hover text-white
// variant='ghost'    → hover:bg-background-elevated text-text-secondary
// variant='danger'   → border border-status-failed/30 text-status-failed hover:bg-status-failed/10
// All: rounded-lg text-sm font-medium transition-colors duration-150
// size='sm': px-3 py-1.5 | size='md': px-4 py-2 (default)
\`\`\`

## Acceptance Criteria
- All 3 variants render with correct colors
- Disabled state: \`opacity-50 cursor-not-allowed\`
- Works as a controlled component" \
  --label "phase:2,type:component"
```

---

### Issue 6: Build StatusBadge component

```bash
gh issue create \
  --title "feat: build statusbadge component" \
  --body "## Task
Create StatusBadge that displays task status with correct color per DESIGN.md Section 5.3.

## Steps
Create \`src/components/agent/StatusBadge.tsx\`:
- Props: \`status: TaskStatus\`
- Use the status color map from DESIGN.md exactly
- RUNNING gets a pulse dot: \`<span className='w-1.5 h-1.5 rounded-full bg-status-running animate-pulse' />\`
- Base classes: \`rounded-full px-2.5 py-0.5 text-xs font-medium inline-flex items-center gap-1.5\`

Status → color mapping:
- RUNNING → \`bg-green-500/10 text-green-400\`
- AWAITING_USER → \`bg-amber-500/10 text-amber-400\`
- QUEUED → \`bg-indigo-500/10 text-indigo-400\`
- COMPLETED → \`bg-background-elevated text-text-muted\`
- FAILED → \`bg-red-500/10 text-red-400\`

## Acceptance Criteria
- Each status renders with correct bg + text color
- RUNNING shows animated pulse dot
- No other status shows the pulse dot" \
  --label "phase:2,type:component"
```

---

### Issue 7: Build Toast notification system

```bash
gh issue create \
  --title "feat: build toast notification system" \
  --body "## Task
Create a toast notification system per DESIGN.md Section 9.

## Steps

### 1. Create \`src/components/ui/Toast.tsx\`
Single toast item: bottom-right fixed, \`bg-background-elevated border border-background-border rounded-xl px-4 py-3\`
Types: 'success' | 'error' | 'warning' | 'info'
Auto-dismiss after 4000ms
Max 3 stacked, gap-2

### 2. Create \`src/context/ToastContext.tsx\`
- State: array of toasts (id, message, type)
- Expose: \`toast.success(msg)\`, \`toast.error(msg)\`, \`toast.warning(msg)\`
- \`addToast\` adds to array, auto-removes after 4s

### 3. Wrap \`<App />\` with \`<ToastProvider />\`

### 4. Create \`src/hooks/useToast.ts\`
Returns the context methods.

## Acceptance Criteria
- \`toast.error('Server error');\` renders toast bottom-right
- Auto-dismisses after 4s
- Max 3 visible at once (oldest removed when 4th added)" \
  --label "phase:2,type:component"
```

---

### Issue 8: Build Skeleton loader component

```bash
gh issue create \
  --title "feat: build skeleton loader component" \
  --body "## Task
Create a Skeleton component for loading states.

## Steps
Create \`src/components/ui/Skeleton.tsx\`:
\`\`\`tsx
// Props: className (for width/height)
// Base: bg-background-elevated animate-pulse rounded-md
// Usage: <Skeleton className='h-4 w-32' />
\`\`\`

Also create:
- \`<SkeletonCard />\` — mimics StatCard shape (h-28 w-full)
- \`<SkeletonRow />\` — mimics a table row (h-12 w-full)

## Acceptance Criteria
- Skeleton animates with pulse
- SkeletonCard and SkeletonRow exist and usable in tables/dashboards" \
  --label "phase:2,type:component"
```

---

## Phase 3 — Dashboard Page

### Issue 9: Build StatCard component

```bash
gh issue create \
  --title "feat: build statcard component" \
  --body "## Task
Build the StatCard component per DESIGN.md Section 5.2.

## Steps
Create \`src/components/dashboard/StatCard.tsx\`:
- Props: \`{ label: string, value: string | number, icon?: ReactNode }\`
- Container: \`bg-background-surface border border-background-border rounded-xl p-5\`
- Icon: top-left, \`text-text-muted\`
- Value: \`text-3xl font-semibold text-text-primary\`
- Label: \`text-xs uppercase tracking-widest text-text-muted mt-1\`

## Acceptance Criteria
- Renders correctly with and without icon
- Value and label styled per spec" \
  --label "phase:3,type:feature"
```

---

### Issue 10: Build Dashboard page with stats and data fetching

```bash
gh issue create \
  --title "feat: build dashboard page with stats" \
  --body "## Task
Build the Dashboard page at route \`/\` using real API data.

## Reference
DESIGN.md Section 7 (Page Inventory), Section 5.2 (StatCard).
API: GET /profile/me (returns stats.total_applied, stats.total_discovered, stats.token_cost)

## Steps

### 1. Create \`src/hooks/useProfile.ts\`
- Calls \`getProfile()\` from api/profile.ts on mount
- Returns: \`{ profile, loading, error }\`

### 2. Update \`src/pages/Dashboard.tsx\`
Layout (vertical, with gap-6):

**Row 1 — Stats (grid-cols-3 gap-4)**
- StatCard: 'Jobs Applied' → profile.stats.total_applied, Briefcase icon
- StatCard: 'Jobs Discovered' → profile.stats.total_discovered, Search icon
- StatCard: 'Tokens Used' → profile.stats.token_cost, Zap icon

While loading: render \`<SkeletonCard />\` × 3

**Row 2 — Section header**
\`text-sm font-semibold uppercase tracking-widest text-text-muted\` → 'Active Tasks'

**Row 3 — TaskTable**
(uses TaskTable component built in Issue 11)

## Acceptance Criteria
- Stats load from /profile/me
- Skeleton shows while loading
- Error state shows toast via useToast" \
  --label "phase:3,type:feature"
```

---

## Phase 4 — Task Management

### Issue 11: Build TaskTable component

```bash
gh issue create \
  --title "feat: build tasktable component" \
  --body "## Task
Build the task list table per DESIGN.md Section 5.3.

## Steps

### 1. Create \`src/hooks/useAgentTasks.ts\`
- Calls \`getTasks()\` from api/agent.ts every 10s (polling fallback)
- Returns: \`{ tasks, loading, refetch }\`

### 2. Create \`src/components/agent/TaskTable.tsx\`
Props: \`{ onViewStream: (task: AgentTask) => void }\`

Table container: \`w-full bg-background-surface border border-background-border rounded-xl overflow-hidden\`
Table header: \`bg-background-elevated text-xs uppercase tracking-widest text-text-muted\`

Columns: ID | Type | Status | Created | Actions

- ID: show first 8 chars of UUID, \`font-mono text-xs\`
- Type: plain text \`text-text-secondary text-sm\`
- Status: \`<StatusBadge status={task.status} />\`
- Created: formatted date, \`text-text-muted text-xs\`
- Actions:
  - Always: \`[View Stream]\` → calls \`onViewStream(task)\`, variant='ghost' size='sm'
  - Only if RUNNING: \`[Stop]\` → calls \`stopTask(task.id)\` then \`refetch()\`, variant='danger' size='sm'

Empty state: centered text 'No tasks yet. Start an agent to begin.' with ghost styling.
Loading state: 4× \`<SkeletonRow />\`

## Acceptance Criteria
- Table renders all tasks with correct columns
- Stop button only visible for RUNNING tasks
- onViewStream called with correct task object" \
  --label "phase:4,type:feature"
```

---

### Issue 12: Build AgentStreamPanel slide-over

```bash
gh issue create \
  --title "feat: build agentstreampanel slide-over component" \
  --body "## Task
Build the Agent Stream Panel per DESIGN.md Section 5.4.

## Steps
Create \`src/components/agent/AgentStreamPanel.tsx\`

Props: \`{ task: AgentTask | null, onClose: () => void }\`

**Container:** fixed right-0 top-0 h-full w-[480px] bg-background-surface border-l border-background-border z-50, slides in from right (use CSS transition on \`translate-x\`)
**Overlay:** semi-transparent black overlay behind panel when open

**Sections:**

1. Header (h-14, flex items-center justify-between px-5 border-b border-background-border):
   - Left: 'Agent Stream' text + task ID (8 chars, mono)
   - Right: StatusBadge + X button (X icon, ghost)

2. Thought Stream (flex-1 overflow-y-auto p-4 gap-1 flex flex-col):
   - Render \`task.metadata.logs\` array
   - Each entry: \`<span className='font-mono text-xs'>\`
   - Color by type: THOUGHT=text-text-secondary, ACTION=text-accent, OBSERVE=text-green-400, ERROR=text-red-400
   - Prefix: '[THOUGHT] ', '[ACTION] ' etc.
   - Auto-scroll to bottom on new entries (\`useEffect\` + \`ref.scrollIntoView\`)
   - Empty: 'No logs yet...' in text-text-muted

3. Screenshot (px-4 pb-4):
   - \`<img src={screenshotUrl}\` where screenshotUrl = \`/agent/tasks/{task.id}/screenshot\`
   - \`rounded-lg border border-background-border w-full object-cover\`
   - Show Skeleton while image loads (use onLoad state)

4. HITL Input (only when task.status === 'AWAITING_USER', px-4 pb-4):
   - Card: \`border border-amber-500/30 bg-amber-500/5 rounded-xl p-4\`
   - Show \`task.metadata.subjective_question\`
   - Textarea + Button 'Send Answer'
   - On submit: call \`sendAnswer(task.id, answer)\` then clear input

## Acceptance Criteria
- Panel slides in/out smoothly
- Logs render with correct colors
- HITL section only shows when AWAITING_USER
- Screenshot loads with skeleton fallback" \
  --label "phase:4,type:feature"
```

---

## Phase 5 — WebSocket Integration

### Issue 13: Build WebSocket context for real-time updates

```bash
gh issue create \
  --title "feat: build websocket context for real-time agent updates" \
  --body "## Task
Connect to WS /ws/{user_id} and update task state in real-time per DESIGN.md Section 8.

## Steps

### 1. Create \`src/context/WebSocketContext.tsx\`
- On mount (after profile loads): open \`new WebSocket(ws://localhost:8000/ws/{user_id})\`
- On message: parse JSON payload, dispatch to listeners
- Expose: \`useWebSocket()\` hook returning \`{ subscribe, unsubscribe }\`
- Auto-reconnect on disconnect (exponential backoff, max 5 retries)
- Cleanup on unmount

Expected WS message shape:
\`\`\`json
{ \"task_id\": \"string\", \"status\": \"RUNNING\", \"log\": { \"type\": \"ACTION\", \"message\": \"...\", \"ts\": \"...\" } }
\`\`\`

### 2. Update \`src/hooks/useAgentTasks.ts\`
- Subscribe to WS messages
- On message: update task in local state by task_id (update status + append log)
- Cancel polling interval if WS connected

### 3. Update \`src/components/layout/Sidebar.tsx\`
- Import useAgentTasks
- Show 'Agent Active' with green pulse if any task has status RUNNING
- Otherwise show 'Agent Idle' with gray dot

### 4. Auto-open AgentStreamPanel
In Dashboard.tsx: if incoming WS message status === AWAITING_USER and panel not open → call onViewStream for that task

## Acceptance Criteria
- Task status updates in table without page refresh
- Sidebar badge reflects live state
- HITL panel auto-opens on AWAITING_USER event" \
  --label "phase:5,type:feature"
```

---

## Phase 6 — Profile & Resume Pages

### Issue 14: Build ResumeUpload component

```bash
gh issue create \
  --title "feat: build resumeupload drag-and-drop component" \
  --body "## Task
Build the resume upload component per DESIGN.md Section 5.5.

## Steps
Create \`src/components/profile/ResumeUpload.tsx\`

States: idle | dragging | uploading | done | error

**Idle:**
- Dashed border: \`border-2 border-dashed border-background-border rounded-xl p-8\`
- Center: Upload icon (lucide) + 'Drag your resume here' + 'PDF or ZIP, max 10MB' subtext
- 'Browse files' button (ghost variant)

**Dragging (onDragOver):**
- \`border-accent bg-accent/5\`

**Uploading:**
- Indeterminate progress bar: \`animate-pulse bg-accent h-1 rounded-full\`

**Done:**
- Filename text (mono) + CheckCircle icon in text-green-400 + 'Re-upload' ghost button

**Error:**
- AlertCircle icon + error message in text-status-failed

Logic:
- Accept \`onDrop\` and \`<input type='file' accept='.pdf,.zip'\>`
- On file selected: call \`uploadResume(file)\` from api/profile.ts
- On success: set state to done, call \`onSuccess()\` callback prop

## Acceptance Criteria
- Drag-over changes border to accent color
- Progress shows during upload
- Done state shows filename + green check
- Error state shows message" \
  --label "phase:6,type:feature"
```

---

### Issue 15: Build Profile page

```bash
gh issue create \
  --title "feat: build profile page" \
  --body "## Task
Build the profile page at route /profile.

## Steps
Create/update \`src/pages/Profile.tsx\`

Layout (max-w-2xl mx-auto, gap-6):

**Section 1 — User Info Card**
- \`bg-background-surface border border-background-border rounded-xl p-5\`
- Section label: 'Account Information'
- Fields: Name (input), Email (disabled input, read-only)
- Save button (primary variant) → calls \`updateProfile()\`

**Section 2 — Resume Card**
- Section label: 'Resume'
- If resume_filename exists: show filename + upload date + 'Replace' option
- \`<ResumeUpload />\` component below

All inputs:
\`bg-background-elevated border border-background-border rounded-lg px-3 py-2 text-sm text-text-primary focus:border-accent focus:outline-none w-full\`

## Acceptance Criteria
- Profile data loads from GET /profile/me
- Name field editable, email read-only
- Save calls PUT /profile/me
- Resume upload works" \
  --label "phase:6,type:feature"
```

---

## Phase 7 — Scrape Trigger & Jobs Page

### Issue 16: Build Jobs page with scrape trigger

```bash
gh issue create \
  --title "feat: build jobs page with scrape trigger" \
  --body "## Task
Build the Jobs page at route /jobs.

## Steps
Create/update \`src/pages/Jobs.tsx\`

**Top bar (flex justify-between items-center mb-6):**
- Left: Page title 'Jobs'
- Right: 'Start Discovery' button (primary) → opens a small inline form

**Scrape Form (shows below top bar when triggered):**
- Label: 'Job Portal URL'
- Input: text input for URL
- Buttons: 'Start Agent' (primary) + 'Cancel' (ghost)
- On submit: call \`startScrape(url)\` → on success: toast.success('Agent started!') + navigate to dashboard

**Task filter tabs (below form):**
- 'All' | 'Running' | 'Completed' | 'Failed'
- Active tab: \`text-accent border-b-2 border-accent\`

**Task Table:**
- Same \`<TaskTable />\` component from Issue 11
- Filter tasks by selected tab status
- \`onViewStream\` opens \`<AgentStreamPanel />\` via state

**AgentStreamPanel** mounted here too (same pattern as Dashboard).

## Acceptance Criteria
- Scrape form shows/hides on button click
- URL submitted to POST /agent/scrape
- Tasks table shows filtered by selected tab
- Stream panel opens on 'View Stream'" \
  --label "phase:7,type:feature"
```

---

## Phase 8 — Polish & Error Handling

### Issue 17: Wire up global 401 redirect and 429 toast

```bash
gh issue create \
  --title "feat: wire up global axios interceptors for 401 and 429" \
  --body "## Task
Add Axios response interceptors per DESIGN.md Section 9.

## Steps
In \`src/api/index.ts\`, add response interceptor:
\`\`\`ts
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const status = error.response?.status;
    if (status === 401) window.location.href = '/login'; // or your auth page
    if (status === 429) toast.error('Too many requests. Wait 60s.');
    if (status === 500) toast.error('Server error. Try again.');
    return Promise.reject(error);
  }
);
\`\`\`

Note: toast here needs to be called outside React tree. Create a standalone \`toastEmitter\` (EventEmitter pattern or a small store) that the ToastProvider listens to.

## Acceptance Criteria
- 401 response redirects to login
- 429 shows toast 'Too many requests. Wait 60s.'
- 500 shows toast 'Server error. Try again.'" \
  --label "phase:8,type:polish"
```

---

### Issue 18: Add loading and empty states across all pages

```bash
gh issue create \
  --title "feat: add loading and empty states across all pages" \
  --body "## Task
Audit all pages and ensure loading + empty states are handled.

## Checklist

### Dashboard
- [ ] Stats row: show SkeletonCard × 3 while loading
- [ ] TaskTable: show SkeletonRow × 4 while loading
- [ ] TaskTable: show empty state if tasks.length === 0

### Jobs
- [ ] TaskTable loading + empty states
- [ ] Scrape form shows loading state on submit (button disabled + spinner)

### Profile
- [ ] Form fields show Skeleton while profile loads
- [ ] ResumeUpload shows current filename or empty state

### AgentStreamPanel
- [ ] Screenshot shows Skeleton while image loads
- [ ] Logs section shows 'No logs yet...' if logs empty

## Acceptance Criteria
- No page shows blank/broken state while data is loading
- Empty states have a message (no blank boxes)" \
  --label "phase:8,type:polish"
```

---

## Issue Execution Order (for Agent)

```
Phase 0: Issues 1 → 2 → 3          (bootstrap, must be sequential)
Phase 1: Issue 4                    (layout)
Phase 2: Issues 5, 6, 7, 8         (primitives, can parallelize)
Phase 3: Issues 9, 10              (dashboard)
Phase 4: Issues 11, 12             (task management)
Phase 5: Issue 13                  (websocket)
Phase 6: Issues 14, 15             (profile)
Phase 7: Issue 16                  (jobs page)
Phase 8: Issues 17, 18             (polish, do last)
```

> ⚠️ **Agent Note:** Phase 0 issues MUST complete in order before anything else. Each issue in later phases should be verified working before moving to the next. If a component is missing that another issue depends on, build the dependency first.
