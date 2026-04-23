ROLE: Senior Software Engineer @ Vanguard. Stack: FastAPI + Postgresql + React JS with Typescript.
MODE: CAVEMAN. Max 2 kalimat di luar code. Zero filler. Zero thinking visible.

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
  TASK: Issue #7 — Migrate ORM from Tortoise to SQLAlchemy 2.0 + Alembic

Description: Current persistence layer pake Tortoise ORM (core/database.py + migrations/models/).
Kita ganti ke SQLAlchemy 2.0 (async) + Alembic untuk migration karena ecosystem lebih kuat, better typing, performance di complex query, dan align sama official FastAPI recommendation.

Todo List

- [ ] Research migration path (Tortoise models → SQLAlchemy declarative models)
- [ ] Update `pyproject.toml` → remove tortoise-orm + aerich, tambah sqlalchemy[asyncio] + alembic + asyncpg
- [ ] Refactor `core/database.py` → SQLAlchemy engine + session factory (async)
- [ ] Convert all models di `migrations/models/` → SQLAlchemy models (modules/profile/, agent/, generator/)
- [ ] Setup Alembic migrations (alembic init + generate initial migration)
- [ ] Update all repository/query logic di modules/ yang pake Tortoise
- [ ] Update dependency injection di FastAPI app

Acceptance Criteria

- All database operations (CRUD profile, agent state, generator) work identically
- Alembic migration berhasil apply ke PostgreSQL
- No Tortoise import tersisa di codebase
- Async support tetap full

START. No deviation. Follow OUTPUT ORDER exactly.

✦ Urutan pengerjaan (prioritas tertinggi ke bawah): 2. #8 (Update README): Sinkronisasi dokumentasi setelah migrasi database. 3. #5 (Testing & Validation): Pastikan semua sistem stabil pasca-migrasi. 4. #9 (UI Component Audit): Audit sebelum bangun halaman spesifik. 5. #10 - #15 (UI Tasks): Bangun UI secara bertahap. 6. #6 (Cleanup & Deployment): Terakhir, bersihkan technical debt dan deploy.
