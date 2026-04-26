# 🛡️ Vanguard: Autonomous AI Job Hunting System

Vanguard is **production-ready full-stack application** bridging job seekers and recruitment systems via autonomous AI agents. Built with **Clean Architecture** for scalability and **Event-Driven Asynchronous Processing** using PostgreSQL as the central backbone.

## 🏗️ Technical Architecture

- **Backend:** FastAPI (Async) + SQLAlchemy 2.0 + Alembic.
- **Persistence:** PostgreSQL (leveraging native row-level locking & asyncpg).
- **Frontend:** React + TypeScript + Tailwind CSS (TailAdmin Base).
- **Automation:** Playwright + MCP (Model Context Protocol).
- **Core Loop:** Orchestrated agentic reasoning powered by **Google Gemini AI**.

## 🔐 Security Framework (Zero Trust)

- **Malware Scanning:** Integrated **VirusTotal/ClamAV** for file integrity.
- **Data Protection:** **AES-256 Encryption** for sensitive credentials and JWT stateless auth.
- **Isolated Execution:** Sandboxed directory handling.

## 🛠️ Tech Stack

- **Language:** Python 3.12+ (Backend) | TypeScript (Frontend)
- **Framework:** FastAPI | React
- **Database:** PostgreSQL (AsyncPG)
- **ORM:** SQLAlchemy 2.0 (Async) + Alembic
- **Automation:** Playwright
- **AI:** Google Gemini SDK
- **UI:** Tailwind CSS (TailAdmin Base)

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
├── UI/             # React + Tailwind Frontend
├── migrations/     # Alembic DB Scripts
└── tests/          # Unit/Integration/E2E Suite
```
