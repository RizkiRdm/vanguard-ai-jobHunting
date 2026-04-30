# AGENTS.md — Vanguard AI Job Hunting System

## PROJECT CONTEXT

### Overview

- **Project name:** Vanguard
- **Purpose:** Autonomous AI agent that finds jobs, tailors CVs, and applies on behalf of a user via browser automation
- **Status:** Active — MVP development
- **Primary language:** Python 3.12
- **Target environment:** Linux server / Docker / Railway or Render

---

## Tech Stack

### Backend

- Runtime: Python 3.12+
- Framework: FastAPI (async)
- Database: PostgreSQL 15+ (asyncpg driver)
- ORM: SQLAlchemy 2.0 (async) + Alembic migrations
- Auth: JWT via python-jose (cookie-based, httponly)
- AI: Google Gemini SDK (`google-genai`) — model `gemini-2.0-flash`
- Browser Automation: Playwright + MCP (Model Context Protocol)
- Logging: structlog (JSON output)
- File scanning: VirusTotal API (httpx)

### Frontend (Minimal Web UI)

- Type: Single-page HTML — no framework, no build step required
- Styling: Plain CSS or inline Tailwind CDN
- Purpose: Monitor agent tasks, view logs, respond to HITL prompts
- NO animations, NO React, NO TypeScript required

### CLI

- Type: Python CLI using `argparse` or `typer`
- Purpose: Start agent, check task status, respond to HITL from terminal
- Entry point: `cli.py`

### Infrastructure

- Container: Docker + Docker Compose
- CI/CD: GitHub Actions (3 jobs: unit, integration, e2e)
- Hosting: Railway or Render (target)

---

## Architecture Overview

- **Pattern:** Layered — Router → Service → Repository (via SQLAlchemy models)
- **API style:** REST under `/api/v1`, plus one WebSocket endpoint at `/agent/ws/{user_id}`
- **Auth flow:** JWT access token (30m) in httponly cookie
- **Background jobs:** Native Python worker loop (`core/worker.py`) polling PostgreSQL with `SELECT FOR UPDATE SKIP LOCKED` — NO external queue (Redis/Celery/TaskIQ not used)
- **AI loop:** ReAct pattern — screenshot → Gemini analysis → browser action → repeat until COMPLETE, AWAIT_USER, FAIL, or max_steps

---

## Project Structure

```
vanguard/
├── core/                   # Shared engine
│   ├── ai_agent.py         # Gemini SDK wrapper + budget check
│   ├── browser.py          # BrowserManager (MCP wrapper)
│   ├── config_manager.py   # YAML config loader (singleton)
│   ├── custom_logging.py   # structlog setup
│   ├── database.py         # SQLAlchemy async engine + session
│   ├── mcp/
│   │   └── mcp_browser.py  # MCP stdio client to Playwright
│   ├── orchestrator.py     # ReAct loop + action dispatch
│   ├── scraper.py          # Google Dorking job search
│   ├── security.py         # JWT, bcrypt, AES-256, VirusTotal
│   ├── task_manager.py     # DB task queue (claim/update)
│   ├── websocket_manager.py
│   └── worker.py           # Main polling worker loop
├── modules/
│   ├── agent/
│   │   ├── agent_router.py
│   │   ├── agent_schemas.py
│   │   └── models.py       # AgentTask, AgentLLMUsageLog
│   ├── generator/
│   │   ├── models.py       # ScrapedJob, TailoredDocument, LLMUsageLog
│   │   └── services.py     # CV tailoring service
│   └── profile/
│       ├── models.py       # User, UserProfile
│       └── profile_router.py
├── shared/
│   └── schemas.py          # Pydantic response models
├── UI/                     # Minimal single-page web UI
│   └── index.html          # ONE FILE — monitor + HITL panel
├── cli.py                  # CLI entry point
├── main.py                 # FastAPI app factory
├── config/
│   └── jobsites.yaml       # Job site selectors + settings
├── migrations/             # Alembic migration scripts
├── prompts/
│   └── agent_prompt.md     # Gemini system prompt
├── docs/
│   ├── BLUEPRINT.md        # Architecture decisions
│   ├── SCHEMA_DB.md        # Database schema reference
│   └── AGENTS.md           # This file
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

---

## Key Commands

```bash
# Install dependencies
uv sync  # or: pip install -e .

# Run dev server
uvicorn main:app --reload --port 8000

# Run worker (separate terminal)
python core/worker.py

# Run CLI
python cli.py --help

# Database migration
alembic upgrade head

# Run all tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# E2E tests (requires running server + DB)
pytest tests/e2e/ -v

# Lint
ruff check . && ruff format .

# Build Docker
docker compose up --build
```

---

## Coding Conventions

### General

- Language: English only — variable names, comments, docstrings, commit messages
- Indentation: 4 spaces, no tabs
- Max line length: 100 characters
- File naming: `snake_case` for all Python files

### Naming

- Variables & functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Async functions: prefix with no special marker — but MUST use `async def` consistently
- Function prefix conventions: `get_`, `create_`, `update_`, `delete_`, `validate_`, `handle_`

### Functions & Classes

- One function = one responsibility
- Max function body: 40 lines (split if longer)
- All function signatures MUST have type hints
- All public methods MUST have a one-line docstring

### Error Handling

- NEVER use bare `except:`
- ALWAYS catch the most specific exception first
- ALWAYS log with context (`self.log.error("event_name", key=value)`) before raising
- Use `structlog` bound logger (`logger.bind(service="name")`) in each class

---

## API Conventions

- Base URL: `/` (no versioning prefix currently — add `/api/v1` when stabilized)
- Auth: JWT in `access_token` cookie (httponly, secure, samesite=lax)
- Response format (success):
  ```json
  { "status": "success", "data": {} }
  ```
- Response format (error):
  ```json
  { "detail": "Human-readable error message" }
  ```
- HTTP codes: 200 GET, 201 POST create, 400 bad input, 401 unauth, 403 forbidden, 404 not found, 429 rate limit

---

## Database Conventions

- Table names: plural, `snake_case` — `agent_tasks`, `user_profiles`, `scraped_jobs`
- Primary key: always `UUID` using `uuid4()` default
- Timestamps: always `created_at` (server_default), `updated_at` (onupdate)
- ORM: **SQLAlchemy 2.0 async ONLY** — do NOT use Tortoise ORM anywhere
- Raw SQL: ONLY allowed in `task_manager.py` for locking patterns (SELECT FOR UPDATE SKIP LOCKED)
- Migrations: MUST have both `upgrade()` and `downgrade()` in every Alembic script
- Optimistic lock: `version` column (Integer) on `users` table — increment on update

### PostgreSQL-Specific Patterns (MAXIMIZE THESE)

- Task claiming: `SELECT FOR UPDATE SKIP LOCKED` — already in `task_manager.py`, DO NOT change
- Budget check: aggregate query with `SUM` on `agent_llm_usage_logs`
- LISTEN/NOTIFY: use for real-time task status push to WebSocket (replaces polling)
- JSONB: use for `meta_data` column — supports indexing if needed later

---

## Security Rules

- NEVER hardcode secrets — all from `.env` via `python-dotenv`
- NEVER commit `.env` — only `.env.example`
- ALWAYS validate file uploads: check MIME type + VirusTotal hash scan
- NEVER expose Python stack traces in API responses (`DEBUG=False` in prod)
- Credentials (job portal username/password): MUST be AES-256 encrypted before DB insert
- PII in logs: ALWAYS use `mask_email()` from `core/security.py`
- JWT: access token 30m, cookie httponly+secure — refresh token NOT yet implemented (out of scope for MVP)

---

## Testing Rules

- Backend: `pytest` + `pytest-asyncio`
- Frontend: none required for minimal HTML UI
- E2E: `playwright` CLI
- Test files: `test_[module].py` in matching `tests/unit/` or `tests/integration/` folder
- Fixtures: use `conftest.py` — NEVER hit production DB
- Use SQLite in-memory or test PostgreSQL for integration tests
- Minimum coverage target: 60% for core modules (`core/security.py`, `core/task_manager.py`, `core/ai_agent.py`)

---

## Git Conventions

- Branch: `feature/issue-{ID}-{short-kebab}`, `fix/issue-{ID}-{short-kebab}`
- Commit: `feat(scope): description - file1.py, file2.py`
- Never commit to `main` directly
- PR must reference the issue number
- Merge only after all CI jobs pass

---

## AI Agent Rules

### MUST

- Read `docs/BLUEPRINT.md` before making any architectural decision
- Place business logic in service layer or orchestrator — NOT in routers
- Use existing `logger.bind(service="name")` pattern in every new class
- Use `AsyncSession` from `core/database.py` for all DB operations
- Check `shared/schemas.py` for existing Pydantic models before creating new ones
- Run `ruff check .` before finishing any task

### MUST NOT

- Use Tortoise ORM — the project uses SQLAlchemy 2.0 async exclusively
- Add `aiopg`, `taskiq`, `redis`, `celery` — not in this architecture
- Import `google.generativeai` — use `google.genai` (the newer SDK)
- Create new files outside the defined structure without asking
- Modify existing Alembic migration files (only create new ones)
- Add animations, complex JS frameworks, or build steps to the UI
- Use `asyncio.sleep` in routers — only in worker/orchestrator
- Change `core/worker.py` polling logic without explicit instruction

### CONTEXT HINTS

- Task queue is PostgreSQL-native — look at `core/task_manager.py` to understand claim logic
- The AI loop is in `core/orchestrator.py` — `_handle_application()` is the ReAct loop
- Browser control goes through `core/mcp/mcp_browser.py` → MCP stdio → Playwright node process
- Config for job sites (selectors, delays) lives in `config/jobsites.yaml` — not hardcoded
- Security functions (encrypt, decrypt, hash, verify) are ALL in `core/security.py`
- WebSocket connections are managed by `core/websocket_manager.py` singleton `manager`

---

## Known Issues / Gotchas

- **ORM split**: Some older scripts (`scripts/`) still use Tortoise ORM. These are broken and should be rewritten to SQLAlchemy. Do NOT use them as reference.
- **`alembic.ini`** has a hardcoded local DB URL — always override with `DATABASE_URL` env var
- **TypeScript proportion**: The `UI/` folder has React/TS scaffolding — this is being replaced by a single `index.html`. Ignore the old React files.
- **`BrowserManager` signature**: `take_screenshot` in orchestrator passes `page` as first arg but the method signature only takes `name`. This is a known bug — fix it in issue #3.
- **`worker.py`** calls `execute_from_worker` with `bound_logger` kwarg but orchestrator doesn't accept it — known bug.
- **Gemini SDK**: `generate_content` is synchronous in some versions — always wrap with `run_in_executor` if you see blocking warnings.
- **`modules/profile/profile_router.py`** still uses Tortoise-style `.get_or_none()` and `.save()` — needs SQLAlchemy migration.
- **Rate limiter in `main.py`** uses an in-memory dict — this resets on restart and won't work multi-process. Acceptable for MVP.

---

## Out of Scope (Do NOT do without explicit instruction)

- Adding Redis, Celery, or any external message queue
- Implementing a multi-tenant system
- Building a mobile app
- Adding payment or subscription logic
- Creating a full React/Next.js frontend
- Implementing refresh token rotation
- Adding file storage to S3 (local `storage/` dir is fine for MVP)
- Changing from cookie-based auth to header-based Bearer tokens
