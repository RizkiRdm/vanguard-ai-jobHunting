ROLE: Senior Software Engineer @ Vanguard. Stack: FastAPI + Postgresql + React JS with Typescript.

OUTPUT ORDER (STRICT):

TESTS:

- UNIT (use pytest for backend and vitest for front end)
- INTEGRATION (use pytest for backend and vitest for front end)
- E2E (use Playwright and Playwright-cli for agent)

Implementation INVALID until all 3 commands PASS.

GIT & GITHUB CLI:

gh issue view {ISSUE ID}
branch: feature/issue-{ISSUE ID}-{short-kebab}
commit: "Issue #{ISSUE ID}: {desc} - file1.php, file2.blade.php" (1 issue = 1 commit)

git checkout -b feature/issue-{ISSUE ID}-{kebab-short-desc}
git add [changed files only]
git commit -m "Issue #{ISSUE ID}: [short desc] - [file1, file2]"
git push -u origin feature/issue-{ISSUE ID}-{kebab-short-desc}

gh pr create --title "feat: Issue #{ISSUE ID} - [task name]" \
 --body "Implements AC. Tests must all pass before merge to main/prod." \
 --base main

gh issue comment 2 --body "Done. PR created. Run {ISSUE ID} test commands above. Merge only after ALL tests PASS."

CONSTRAINTS (HARD):

- Follow BLUEPRIN.md & ux_doc.md strictly. New files: add "// Ref: BLUEPRIN.md & ux_doc.md" at top.
- Clean Code only. No scope creep.
- 1 issue = 1 commit.
- CI enforced via .github/workflows/ci.yml (3 separate jobs: unit-test, integration-test, e2e-test). Merge to main/prod ONLY if all jobs PASS.
- Reuse existing code. Ambiguous → safest assumption per DESIGN.md.
- All 3 tests must PASS before merge.
- merge to branch when all test passed and delete current branch
  TASK: Issue #9 — UI Component Audit & Standardization (React + Tailwind)

Description: UI folder pake React + Tailwind (sudah migrate ke TailAdmin).
Fokus bukan bikin UI baru, tapi audit & standardize pemakaian existing components saja.
Ikutin flow dari sisa wireframe/UX document yang masih ada + current unfinished UI.
Tujuannya: consistency, reusability, dan maintainability component.

Todo List

- [ ] Audit semua component di UI/ (list apa saja yang dipakai: Button, Card, Input, Table, Modal, Sidebar, Dashboard, JobCard, dll)
- [ ] Document component usage di README (atau buat components.md)
- [ ] Standardize props, styling (Tailwind classes), dan naming convention
- [ ] Fix inconsistency di component yang sudah dipakai di pages yang belum beres
- [ ] Pastikan semua component follow TailAdmin pattern (jika ada)
- [ ] Align component flow dengan existing UX/wireframe (login → dashboard → agent monitoring → job apply flow)

Acceptance Criteria

- Semua component ter-audit dan didokumentasikan
- No duplicate logic atau inconsistent styling di UI yang sudah ada
- Flow UI mengikuti wireframe/UX yang tersisa tanpa bikin halaman baru
- Code clean, reusable, dan easy buat continue development

START. No deviation. Follow OUTPUT ORDER exactly.
