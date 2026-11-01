# Vanguard UI System

Single source of truth for colours, typography, spacing, components and responsive
rules in `apps/web`. Tokens live in `apps/web/src/app.css`; this file explains what
they mean and when to use them. If code and this file disagree, fix one of them in
the same change.

Visual reference: `vanguard-ui-system.html` at the repository root. It is a static
prototype with demo content. Never copy its sample records, metric counts or names
into the app, and never link to it as a product route.

Non-goals: new screens, new API calls, new dependencies, backend changes. The system
describes the existing UI only.

## Colours

| Token         | Value                       | Role                                    |
| ------------- | --------------------------- | --------------------------------------- |
| `--void`      | `#0b0c0e`                   | Page background                         |
| `--graphite`  | `#131416`                   | Panels, cards, auth card                |
| `--charcoal`  | `#1f1f21`                   | Inputs, nested surfaces                 |
| `--smoke`     | `#3c3d3e`                   | Reserved for heavier separators         |
| `--steel`     | `#71717a`                   | Metadata labels, hints, footer text     |
| `--fog`       | `#858687`                   | Secondary body text, descriptions       |
| `--ash`       | `#9d9e9f`                   | Tertiary text, quiet badges             |
| `--chalk`     | `#cececf`                   | Secondary headings, labels              |
| `--snow`      | `#ffffff`                   | Primary text                            |
| `--bone`      | `#f2f2f2` with `--ink` text | Primary action fill                     |
| `--blue`      | `#3b82f6`                   | Reserved accent                         |
| `--arc-blue`  | `#60a5fa`                   | Links, queued/running state, active nav |
| `--ring-blue` | `#93c5fd`                   | Focus ring                              |
| `--mint`      | `#4ade80`                   | Success                                 |
| `--coral`     | `#f87171`                   | Error, destructive                      |
| `--amber`     | `#fbbf24`                   | `waiting_for_user` only                 |
| `--hairline`  | `rgba(255,255,255,.07)`     | Borders (0.5px), dividers               |
| `--soft-fill` | `rgba(255,255,255,.05)`     | Hover fill on quiet controls            |

Rules:

- Dark only. `color-scheme: dark` is set in `app.html`; there is no light variant.
- Blue is an accent, never a CTA fill. Primary actions are bone with ink text.
- Amber is semantic: `waiting_for_user` and approval panels. Do not use it decoratively.
- No gradients, no coloured glows, no shadows except `--shadow-card`.

## Typography

- Stack: `Inter` when installed locally, otherwise the system sans stack. No webfont
  request; adding a network font is a dependency change.
- Headlines use weight 400. Emphasis comes from size and colour, not bold shouting.
- Body and UI text 11-14px, weights 400-480.

| Element        | Size                                       | Notes                        |
| -------------- | ------------------------------------------ | ---------------------------- |
| `h1`           | `clamp(32px, 7vw, 52px)`, line-height 1.02 | Page titles only             |
| `h2`           | 22px (18px inside a panel header)          | Section and panel titles     |
| `h3`           | 15px, weight 480                           | Card titles                  |
| body           | 14px, line-height 1.45                     |                              |
| `.lead`        | 14px, `--fog`, max-width 560px             | Intro paragraph under an h1  |
| `.small`       | 11px                                       |                              |
| `.micro`       | 10px                                       | Metadata only, never content |
| labels / hints | 11px / 10px                                |                              |

Letter-spacing: `-.045em` on `h1`, `-.035em` on `h2`, normal on body.

## Spacing, radius, layout

- Base unit 4px. Used gaps: 8, 12, 14, 16, 24, 32px.
- Radius: 10px controls, 12px panels, 16px the auth card, `--radius-pill` for pills.
  Do not mix a second radius scale into the same screen.
- Content max-width `--content-width` (1080px), centred, page padding 16px (24px above
  620px).
- Two-column layouts appear at 620px, not before. Mobile is the design, not the fallback.
- Never set a fixed pixel width on a form or panel so it only works on desktop.

## Components

CSS classes are the component library. There is one Svelte component,
`StatusBadge.svelte`, because the status-to-rule mapping must exist once. Do not add
a wrapper component for a class that already exists.

### Buttons (`button`, `a.btn`)

- `btn btn-primary` — bone fill, ink text. The one action that moves work forward.
- `btn btn-secondary` — dark fill, hairline border. Supporting actions.
- `btn btn-quiet` — transparent, hairline border. Navigation-ish actions, sign out.
- `btn btn-danger` — coral text and border. Destructive only (remove resume).
- `btn-small` reduces height to 31px for inline actions.
- Minimum interactive height 38px (31px small). Never smaller on touch screens.
- Disabled: 50% opacity, `cursor: not-allowed`. A pending action must say what it is
  doing ("Uploading…", "Working…") rather than only grey out.

### Panels (`section.panel`)

Graphite surface, 0.5px hairline, 12px radius, 18-22px padding. Header is
`.panel-header` with `.panel-title` and optional `.panel-description`. A panel holds
one concern. Do not nest a panel inside a panel.

### Forms

- `label` above the control, `.field-hint` on the right of the label for limits,
  `.field-footer` below for guidance.
- Inputs and textareas: `--charcoal` fill, 41px minimum height, 9px radius.
- Focus = border `rgba(147,197,253,.65)` plus the global focus ring.
- Invalid state uses `aria-invalid="true"`, which turns the border coral.
- No placeholder-as-label. Labels stay visible.

### Feedback (`p.form-status`)

- `.form-status` neutral, `.success`, `.error`, `.info`.
- Error feedback uses `role="alert"`; success and info use `role="status"`.
- Feedback appears above the form it belongs to, not at the bottom of the page.
- Empty states use `.empty-state`: honest sentence plus, where useful, one action.

### Task list

`.task-list` of `.task-card`. Each card shows type, status badge and creation time on
mobile; nothing collapses into a table. All six statuses come from `StatusBadge`.

### Task detail

`.task-summary` for status and metadata via `.data-label` / `.data-value`.
`.approval-panel` for the gate, always stating that nothing has been submitted.
Raw payload, result and approval details live behind `<details class="json-details">`;
summary first, JSON never the primary content.

### Listings

`.listing-card` per job: title link (`rel="noreferrer noopener"`, `target="_blank"`),
company and location when present, description as text. Never invent salary, match
score or freshness.

### Login

`.auth-wrap` > `.auth-card`. Mode switch is `.auth-switch` with `aria-pressed`.
No app navigation on this screen.

## Responsive

- Mobile first, from 320px. Every view must survive 320px without horizontal scroll.
- 620px: two-column dashboard and profile layouts, wider page padding.
- 900px: more panel padding, auth card vertical margin.
- Tables are never the only layout for a list.
- Long job titles and URLs wrap (`overflow-wrap: anywhere`), never clip.

## Accessibility

- Visible focus on every interactive element, via `:focus-visible` and `--focus-ring`.
- Nav links carry `aria-current="page"` when active.
- Form controls have a real `label` tied by `id`/`for`.
- Async feedback is announced: `role="alert"` for errors, `role="status"` for results.
- Colour is never the only signal; text states the meaning.
- `prefers-reduced-motion` disables transitions and animations.
- `aria-live` regions must not contain a whole page; scope them to the message.

## States we must show honestly

- Loading: button text changes and disables; no fake progress bars.
- Empty: `.empty-state` explains what will appear and why it is empty.
- Error: `.form-status.error` with the server message, or the SvelteKit error page.
- Success: the state the API returned, never an invented outcome.
- Approval: `waiting_for_user` means the agent stopped. Approving re-queues the task;
  it does not mean an employer received an application.

## Anti-patterns

- Inline `style=` for colour, spacing or layout that a class already covers.
- Light-mode values, ad-hoc hex codes outside the token list.
- Metric cards, counts, completeness scores or any number the API does not return.
- `{@html}` for job content or AI output.
- Animations beyond a 150ms background or border transition.
