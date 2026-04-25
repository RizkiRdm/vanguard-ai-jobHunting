# Vanguard Frontend Design System

**Stack:** React + Vite, Tailwind CSS v3, Lucide React (icons)
**Theme:** Clean & Modern SaaS — Dark Mode
**Aesthetic Direction:** Obsidian SaaS — deep neutrals, razor-sharp typography, intentional accent color, zero noise.

---

## 1. Design Philosophy

Vanguard is a power tool for job hunters. The UI must feel like a **professional command center**, not a chatbot toy. Every element earns its place. The user should feel in control.

Core principles:
- **Density without clutter** — show meaningful data, not empty states
- **Status is king** — the agent's state (RUNNING / AWAITING / DONE) must be immediately obvious at a glance
- **Trust through transparency** — the AI's thought stream and screenshots are first-class UI elements, not modals buried in settings

---

## 2. Color Palette

All colors defined as Tailwind custom config in `tailwind.config.js`.

```js
// tailwind.config.js — extend colors
colors: {
  background: {
    DEFAULT: '#0A0A0F',   // near-black base
    surface: '#111118',   // card surfaces
    elevated: '#1A1A24',  // hover / elevated cards
    border: '#2A2A38',    // borders
  },
  accent: {
    DEFAULT: '#6366F1',   // indigo-500 — primary CTA
    hover: '#4F46E5',     // indigo-600
    muted: '#6366F120',   // accent with 12% opacity (background tints)
  },
  text: {
    primary: '#F1F1F5',
    secondary: '#9090A8',
    muted: '#5A5A72',
  },
  status: {
    running:   '#22C55E',   // green
    awaiting:  '#F59E0B',   // amber
    queued:    '#6366F1',   // indigo
    completed: '#9090A8',   // muted gray
    failed:    '#EF4444',   // red
  }
}
```

**Usage rules:**
- `background.DEFAULT` → `<body>`, page root
- `background.surface` → cards, sidebars, panels
- `background.elevated` → hover states, dropdowns
- `accent.DEFAULT` → primary buttons, active nav, links
- Never use pure white (`#FFF`) — use `text.primary` max

---

## 3. Typography

```js
// tailwind.config.js — fontFamily
fontFamily: {
  sans: ['DM Sans', 'sans-serif'],       // body, UI labels
  mono: ['JetBrains Mono', 'monospace'], // agent logs, thought stream, code
}
```

**Load via Google Fonts** in `index.html`:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

**Type scale (Tailwind classes):**

| Role | Class |
|---|---|
| Page title | `text-2xl font-semibold tracking-tight` |
| Section header | `text-sm font-semibold uppercase tracking-widest text-text-muted` |
| Body | `text-sm font-normal text-text-secondary` |
| Label | `text-xs font-medium text-text-muted` |
| Mono / log | `font-mono text-xs text-text-secondary` |
| Stat number | `text-3xl font-semibold text-text-primary` |

---

## 4. Spacing & Layout

- Base unit: `4px` (Tailwind default)
- Page max-width: `1280px`, centered (`max-w-screen-xl mx-auto`)
- Content padding: `px-6` on mobile, `px-8` on lg+
- Card internal padding: `p-5` (20px)
- Gap between cards: `gap-4` or `gap-6`

**Layout: fixed sidebar + main content area**
```
┌─────────────────────────────────────────────────────────┐
│  Sidebar (w-56, fixed left)  │  Main Content (flex-1)   │
│  - Logo                      │  - Header bar            │
│  - Nav items                 │  - Page content          │
│  - Agent status dot          │                          │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Component Specs

### 5.1 Sidebar (`<Sidebar />`)

```
Width: w-56 (224px), fixed, full height
Background: bg-background-surface
Border: border-r border-background-border
```

Elements (top to bottom):
1. **Logo area** — `h-16`, Vanguard wordmark `text-text-primary font-semibold` + shield icon
2. **Nav items** — icon + label, `rounded-lg px-3 py-2`
   - Active: `bg-accent-muted text-accent` 
   - Inactive: `text-text-secondary hover:bg-background-elevated hover:text-text-primary`
3. **Agent Status Badge** (bottom of sidebar) — dot + label
   - Running: green pulse dot + "Agent Active"
   - Idle: gray dot + "Agent Idle"

Nav items:
- Dashboard → `/`
- Jobs → `/jobs`
- Profile → `/profile`
- Settings → `/settings`

---

### 5.2 Stat Card (`<StatCard />`)

```
Props: { label: string, value: string|number, icon?: ReactNode, trend?: string }
Background: bg-background-surface
Border: border border-background-border
Border-radius: rounded-xl
Padding: p-5
```

Layout:
```
┌───────────────────────────────┐
│  [icon]           [trend]     │
│                               │
│  342                          │  ← text-3xl font-semibold
│  Jobs Applied                 │  ← text-xs uppercase tracking-widest text-muted
└───────────────────────────────┘
```

---

### 5.3 Task Table (`<TaskTable />`)

Columns: `ID (truncated 8 chars)` | `Type` | `Status` | `Created` | `Actions`

**Status badge** (`<StatusBadge status={...} />`):
```
RUNNING   → bg-status-running/10  text-status-running   + pulse dot
AWAITING  → bg-status-awaiting/10 text-status-awaiting
QUEUED    → bg-status-queued/10   text-status-queued
COMPLETED → bg-background-elevated text-text-muted
FAILED    → bg-status-failed/10   text-status-failed
```

All badges: `rounded-full px-2.5 py-0.5 text-xs font-medium inline-flex items-center gap-1.5`

Actions per row:
- `[View Stream]` → opens Agent Stream Panel (slide-over)
- `[Stop]` → only visible if status = RUNNING, calls `POST /tasks/{id}/stop`

---

### 5.4 Agent Stream Panel (`<AgentStreamPanel />`)

A **slide-over panel** from the right (not a modal). Width: `w-[480px]`.

Sections (top to bottom):
1. **Header** — Task ID + status badge + `[X]` close button
2. **Thought Stream** — scrollable feed, monospace font
   ```
   [THOUGHT]  Navigating to apply page...
   [ACTION]   CLICK → button.easy-apply
   [OBSERVE]  Page changed to confirmation screen
   ```
   Each line: `font-mono text-xs`, color-coded by type:
   - `[THOUGHT]` → `text-text-secondary`
   - `[ACTION]`  → `text-accent`
   - `[OBSERVE]` → `text-status-running`
   - `[ERROR]`   → `text-status-failed`

3. **Screenshot Viewer** — `<img>` loaded from `GET /agent/tasks/{id}/screenshot`
   - Lazy loaded, click to expand full-size
   - Shows skeleton while loading

4. **HITL Input** (only visible when `status === 'AWAITING_USER'`)
   ```
   ┌─────────────────────────────────────────────┐
   │ [!] Agent needs your input                  │
   │ "What is your expected notice period?"      │
   │ [________________________] [Send Answer]    │
   └─────────────────────────────────────────────┘
   ```
   - Yellow/amber accent border on card
   - Calls `POST /agent/interact/{task_id}`

---

### 5.5 Resume Upload (`<ResumeUpload />`)

Drag-and-drop zone. Accepts `.pdf`, `.zip`.

States:
- **Idle** → dashed border `border-background-border`, upload icon + "Drag your resume here"
- **Dragging** → `border-accent bg-accent-muted` 
- **Uploading** → progress bar (indeterminate)
- **Done** → file name + green checkmark + "Re-upload" link

Calls `POST /profile/resume`.

---

### 5.6 Primary Button (`<Button />`)

```
variant="primary"  → bg-accent hover:bg-accent-hover text-white
variant="ghost"    → bg-transparent hover:bg-background-elevated text-text-secondary
variant="danger"   → bg-transparent hover:bg-status-failed/10 text-status-failed border border-status-failed/30
```

All: `rounded-lg px-4 py-2 text-sm font-medium transition-colors duration-150`

---

## 6. Interaction & Motion

Keep it **subtle**. This is a professional tool, not a landing page.

- Page transitions: `opacity-0 → opacity-100` over `150ms`
- Sidebar nav active: instant, no animation needed
- Cards on hover: `transition-colors duration-150` only (no scale/lift)
- Agent stream new entries: slide in from bottom `translate-y-2 opacity-0 → translate-y-0 opacity-100` over `200ms`
- Status pulse dot (RUNNING): CSS `animate-pulse` on the dot only

**No scroll animations. No entrance animations on static content.**

---

## 7. Page Inventory

| Route | Page | Key Components |
|---|---|---|
| `/` | Dashboard | `StatCard × 4`, `TaskTable`, `ResumeUpload` |
| `/jobs` | Job List | Table of discovered jobs, filter by status |
| `/profile` | Profile | User info form, resume status |
| `/settings` | Settings | (placeholder for now) |

---

## 8. WebSocket Integration (`/ws/{user_id}`)

The frontend maintains a **single persistent WS connection** after login.

On message received, update:
1. Task status in `TaskTable`
2. Append new thought/action to open `AgentStreamPanel`
3. If status → `AWAITING_USER`: auto-open `AgentStreamPanel` + show HITL input

Use a global WS context (`WebSocketContext`) so any component can subscribe without prop-drilling.

---

## 9. Error Handling (UI)

| HTTP Status | UI Response |
|---|---|
| `401` | Redirect to login |
| `429` | Toast: "Too many requests. Wait 60s." |
| `422` | Inline field error |
| `500` | Toast: "Server error. Try again." |

Toast component: bottom-right, auto-dismiss after 4s, max 3 stacked.

---

## 10. File Structure (Frontend)

```
frontend/
├── public/
├── src/
│   ├── api/              # Axios instance + typed API functions
│   │   ├── agent.ts
│   │   ├── profile.ts
│   │   └── index.ts
│   ├── components/
│   │   ├── ui/           # Primitives: Button, Badge, Toast, Skeleton
│   │   ├── layout/       # Sidebar, AppShell
│   │   ├── agent/        # AgentStreamPanel, TaskTable, StatusBadge
│   │   ├── dashboard/    # StatCard
│   │   └── profile/      # ResumeUpload
│   ├── context/
│   │   └── WebSocketContext.tsx
│   ├── hooks/
│   │   ├── useAgentTasks.ts
│   │   └── useProfile.ts
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Jobs.tsx
│   │   ├── Profile.tsx
│   │   └── Settings.tsx
│   ├── types/
│   │   └── index.ts      # AgentTask, Profile, TaskStatus enums
│   ├── App.tsx
│   └── main.tsx
├── index.html
├── tailwind.config.js
└── vite.config.ts
```
