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

```

---

### Issue 2: Configure Tailwind with Vanguard design tokens

```bash

```

---

### Issue 3: Create TypeScript types and API client

```bash

```

---

## Phase 1 — Layout & Navigation

### Issue 4: Build AppShell layout with Sidebar

```bash

```

---

## Phase 2 — UI Primitives

### Issue 5: Build Button primitive component

```bash

```

---

### Issue 6: Build StatusBadge component

```bash

```

---

### Issue 7: Build Toast notification system

```bash

```

---

### Issue 8: Build Skeleton loader component

```bash

```

---

## Phase 3 — Dashboard Page

### Issue 9: Build StatCard component

```bash

```

---

### Issue 10: Build Dashboard page with stats and data fetching

```bash

```

---

## Phase 4 — Task Management

### Issue 11: Build TaskTable component

```bash

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
- Screenshot loads with skeleton fallback"
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
- HITL panel auto-opens on AWAITING_USER event"
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
- Error state shows message"
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
- Resume upload works"
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
- Stream panel opens on 'View Stream'"
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
- 500 shows toast 'Server error. Try again.'"
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
- Empty states have a message (no blank boxes)"
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
