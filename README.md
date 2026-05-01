# 🛡️ Vanguard: Autonomous AI Job Hunting System

Vanguard is an **autonomous AI job hunting system**. It finds relevant jobs, tailors your CV, and submits applications automatically via browser automation. Built with **Clean Architecture** and **Event-Driven Asynchronous Processing** using PostgreSQL as the central backbone.

## 🏗️ Technical Architecture

- **Backend:** FastAPI (Async) + SQLAlchemy 2.0 + Alembic.
- **Persistence:** PostgreSQL (leveraging native row-level locking & asyncpg).
- **Frontend:** Minimalist single-page HTML (no build step).
- **Automation:** Playwright + MCP (Model Context Protocol).
- **Core Loop:** Orchestrated agentic reasoning powered by **Google Gemini AI**.

## 🔐 Security Framework

- **Malware Scanning:** VirusTotal API integration for resume safety.
- **Data Protection:** AES-256 encryption for credentials and JWT stateless auth.
- **Isolated Execution:** Secure storage for resume files.

## 🛠️ Tech Stack

- **Language:** Python 3.12+
- **Framework:** FastAPI
- **Database:** PostgreSQL 15+ (asyncpg)
- **ORM:** SQLAlchemy 2.0 (Async) + Alembic
- **Automation:** Playwright
- **AI:** Google Gemini SDK (`google-genai`)
- **Logging:** `structlog` (JSON output)
- **UI:** Plain HTML + Tailwind CSS CDN

## 💿 Database Setup

Vanguard utilizes PostgreSQL native features for task queuing and state management.

1. Ensure PostgreSQL is running.
2. Set `DATABASE_URL` in `.env` (e.g., `postgresql+asyncpg://user:pass@host:port/dbname`).
3. Run migrations: `alembic upgrade head`.

## 📁 Project Structure

```tree
/
├── core/           # Backend Engine (DB, Security, AI, Browser)
├── modules/        # Domain Logic (Profile, Agent, Generator)
├── UI/             # Single-page HTML Monitoring Interface
├── migrations/     # Alembic DB Scripts
└── tests/          # Unit/Integration/E2E Suite
```
