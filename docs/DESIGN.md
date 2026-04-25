# Design System: Vanguard AI — Obsidian SaaS

## 1. Visual Theme & Atmosphere

Dark-mode command center for an autonomous AI job-hunting agent. Built for power users who need to monitor, control, and trust a bot doing work on their behalf. The UI must communicate precision, real-time awareness, and control — not friendliness or marketing.

- **Density:** 6/10 — Functional, data-forward
- **Variance:** 3/10 — Consistent system, deliberate hierarchy
- **Motion:** 3/10 — Purposeful only (status changes, stream entries, panel transitions)

---

## 2. Color Palette & Roles

- **Deep Black** (`#0A0A0F`) — Base page background
- **Surface** (`#111118`) — Card and panel backgrounds
- **Elevated** (`#1A1A24`) — Hover states, table row hover, dropdowns
- **Border** (`#2A2A38`) — All borders, dividers, separators
- **Indigo** (`#6366F1`) — Primary accent: CTAs, active nav, focus rings, links
- **Indigo Muted** (`#6366F114`) — Accent background tints (badges, highlights)
- **Text Primary** (`#F1F1F5`) — Headings, values, primary content
- **Text Secondary** (`#9090A8`) — Body text, descriptions, table content
- **Text Muted** (`#5A5A72`) — Labels, captions, placeholders, section headers
- **Green** (`#22C55E`) — RUNNING status, success states, live indicators
- **Amber** (`#F59E0B`) — AWAITING_USER status, warnings, HITL alerts
- **Red** (`#EF4444`) — FAILED status, error states, destructive actions

---

## 3. Typography Rules

- **UI / Interface:** DM Sans — Weight 400/500/600, used for all labels, body, nav, buttons
- **Stat Values / Headings:** DM Sans — Weight 600, tight tracking, used for numbers and page titles
- **Section Labels:** DM Sans — Weight 600, `0.7rem`, uppercase, `0.12em` letter-spacing, `Text Muted` color
- **Monospace / Logs:** JetBrains Mono — Weight 400/500, used exclusively for agent thought stream, task IDs, log entries, code

**Font loading:** Google Fonts via `<link>` in `index.html`
```
DM Sans: wght@400;500;600
JetBrains Mono: wght@400;500
```

Scale:
- Page Title: `1.5rem` / weight 600 / tight tracking
- Stat Value: `2rem` / weight 600
- Body: `0.875rem` / 1.6 line-height
- Label / Caption: `0.75rem` / weight 500
- Mono (logs): `0.75rem` / 1.7 line-height

---

## 4. Component Stylings

- **Primary Button:** `4px` radius. Indigo fill (`#6366F1`). Hover: `#4F46E5`. Active: 1px downward translate. Weight 500. No glow, no shadow.
- **Ghost Button:** Transparent fill. `text-secondary`. Hover: `bg-elevated`. No border. Same radius.
- **Danger Button:** Transparent fill. `1px border` in `red/30` opacity. `text-red`. Hover: `bg-red/10`. Same radius.
- **Cards / Panels:** `6px` radius. `Surface` background. `1px border` in `Border` color. No box-shadow — depth comes from color layering alone.
- **Table:** `Surface` background. `1px border` outer. Header row: `Elevated` background. Row hover: `Elevated` background transition `150ms`. No row separators between data rows — use breathing room (padding) instead.
- **Inputs / Textareas:** `4px` radius. `Elevated` background. `1px border` in `Border`. Focus: border shifts to `Indigo`. No floating labels — label always above. Error text below in `Red`.
- **Status Badges:** `9999px` radius (pill). Background is status color at `10%` opacity. Text is status color. `0.7rem` font, weight 500. RUNNING badge includes `6px` circle with `animate-pulse`.
- **Skeletons:** `Elevated` background with `animate-pulse`. Match exact dimensions of target component. No spinners anywhere.
- **Sidebar Nav Items:** `6px` radius. Active: `Indigo Muted` background + `Indigo` text. Inactive: `text-secondary`, hover `Elevated` background + `text-primary`. Icon + label inline, `gap-2.5`.
- **Toast Notifications:** Fixed bottom-right. `Surface` background. `1px Border`. `6px` radius. `text-sm`. Auto-dismiss 4s. Stack max 3, `gap-2`. Slide in from right `200ms ease-out`.
- **Agent Stream Entries:** `font-mono text-xs`. Prefixed by type tag. THOUGHT: `text-secondary`. ACTION: `text-indigo`. OBSERVE: `text-green`. ERROR: `text-red`. Each entry fades in from `translateY(6px)` over `180ms`.
- **HITL Alert Card:** `Amber/30` border. `Amber/5` background. `6px` radius. Visually distinct from all other surfaces — must feel urgent but not alarming.
- **Slide-Over Panel:** `480px` fixed width, right-anchored, full height. `Surface` background. `1px border-l Border`. Backdrop: `black/40` overlay. Enters via `translateX(100%) → translateX(0)` over `250ms ease-out`.

---

## 5. Layout Principles

- **Shell:** Fixed sidebar (`224px` wide) + scrollable main content (`flex-1`). Full `100dvh` height. No top navbar.
- **Grid:** CSS Grid / Flexbox. Max-width `1280px` centered, `2rem` side padding on desktop, `1rem` on mobile.
- **Spacing rhythm:** Base unit `4px`. Standard internal card padding: `20px`. Gap between cards: `16px` or `24px`. Section vertical gap: `32px`.
- **Stat row:** 3-column grid on desktop, stacks to 1-column below `640px`.
- **Table columns:** Fixed widths — ID (`96px`), Type (`100px`), Status (`140px`), Created (`140px`), Actions (`auto`).
- **Mobile collapse:** Sidebar collapses to icon-only or hidden drawer below `768px`. All tables scroll horizontally.
- **z-index contract:** base (`0`) / sidebar (`10`) / slide-over backdrop (`40`) / slide-over panel (`50`) / toast (`100`).

---

## 6. Motion & Interaction

- **Physics:** `ease-out`, `150–250ms` for UI transitions. `ease-in-out` for panel entry/exit only.
- **Sidebar nav:** Instant active state. No animation.
- **Status badge changes:** Color crossfade `200ms`. Pulse dot uses `animate-pulse` CSS only.
- **Card hover:** `background-color` transition `150ms ease-out` only. No scale, no lift, no shadow change.
- **Slide-over panel:** Enter `translateX(100%) → 0` over `250ms ease-out`. Exit reverse `200ms ease-in`.
- **Agent stream new entries:** `opacity: 0, translateY: 6px → opacity: 1, translateY: 0` over `180ms ease-out`. Auto-scroll to bottom.
- **Toast:** Slide in from right `200ms ease-out`. Fade out `150ms ease-in` on dismiss.
- **Page transitions:** None. Instant. This is a tool, not a marketing site.
- **Performance rule:** Only `transform` and `opacity` animated. No `height`, `width`, or layout properties.

---

## 7. Anti-Patterns (Banned)

- No emojis in UI — Lucide React icons only
- No pure white (`#FFFFFF`) anywhere — use `Text Primary` (`#F1F1F5`) max
- No box-shadows for depth — use color layering (`Surface` → `Elevated` → `Border`)
- No `h-screen` — use `min-h-[100dvh]` or `h-[100dvh]` with overflow control
- No page load animations on static content — motion only for dynamic/live elements
- No purple gradients, glassmorphism, or glow effects
- No generic SaaS copy: "Powerful", "Seamless", "Supercharge", "Next-Gen"
- No circular avatar placeholders for non-user content
- No three equal-width columns for feature content — this is a tool UI, not a landing page
- No inline `style=` for colors — all colors via Tailwind utility classes mapped to CSS variables
