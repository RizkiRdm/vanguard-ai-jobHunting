# 🛡️ Vanguard: Autonomous AI Job Hunting API

Vanguard is a high-performance **Backend API** designed as an autonomous agent to bridge the gap between job seekers and automated recruitment systems. Built with a **Modular MVC / Asynchronous Architecture**, Vanguard acts as a "Digital Twin" to navigate, analyze, and apply for roles via headless browsers.

## 🏗️ Technical Architecture
Developed with **Clean Architecture** and **Asynchronous I/O** at its core:
- **Core Engine:** FastAPI for high-concurrency request handling.
- **Asynchronous Processing:** Leveraging Python's `asyncio` for non-blocking browser interactions and AI reasoning loops powered by **TaskIQ**.
- **Agentic Logic:** A "Reasoning Loop" (Observe -> Think -> Act) powered by **Google Gemini AI** and **Playwright**.
- **Persistence Layer:** PostgreSQL with **SQLAlchemy 2.0 (Async)**, utilizing **Alembic** for schema migrations and versioned state management.

## 🔐 Security Framework (Zero Trust)
- **Malware Scanning:** Integrated **VirusTotal/ClamAV** for scanning uploaded documents before storage.
- **Data Protection:** **AES-256 Encryption** for sensitive portal credentials and JWT for stateless authentication.
- **Isolated Execution:** Sandboxed directory handling for file extractions.

## 🛠️ Tech Stack
* **Language:** Python 3.12+
* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (Async) + Alembic
* **Task Queue:** TaskIQ
* **Automation:** Playwright
* **AI Integration:** Google Gemini SDK
* **Frontend:** React + Tailwind CSS (TailAdmin Base)
* **Security:** ClamAV, AES-256

## 💿 Database Setup
Vanguard uses SQLAlchemy 2.0 with asyncpg.
1. Ensure PostgreSQL is running.
2. Set `DATABASE_URL` in `.env` (e.g., `postgresql+asyncpg://user:pass@host:port/dbname`).
3. Run migrations: `alembic upgrade head`.

## 🎨 Frontend / UI
Vanguard uses a modern dashboard built with React and Tailwind CSS.
- **Component Library:** Custom library located in `UI/src/components/`.
- **Core Components:** `Button`, `Card`, `Table`, `Modal`, `Form`, `DashboardLayout`.
- **Styling:** Consistent Tailwind utility classes.
- **Best Practices:** Prefer component composition, naming follows `PascalCase`, props documented in component files.

## 📁 Project Structure
``` tree
vanguard-app/
├── core/                       # Shared Engine
│   ├── database.py             # SQLAlchemy Async Engine/Session
│   ├── security.py             # AES-256 & PII Masking
│   ├── ai_engine.py            # Gemini SDK
│   ├── browser.py              # Playwright Worker Setup
│   └── malware_scan.py         # Scanner Wrapper
├── modules/                    # Business Domains
│   ├── profile/                # User Profile Logic
│   ├── agent/                  # AI Agent Tasks/WS
│   └── generator/              # Document Generation
├── UI/                         # Frontend App
│   ├── src/components/         # UI Component Library
│   └── ...
├── shared/                     # The Contract
│   └── schemas.py              # Pydantic (Input/Output Validation)
├── tests/                      # Testing Suite (Pytest + Vitest)
├── migrations/                 # Alembic Migrations
├── main.py                     # App Entry Point
└── .env.example
```
