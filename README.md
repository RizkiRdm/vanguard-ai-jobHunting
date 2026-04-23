# 🛡️ Vanguard: Autonomous AI Job Hunting API

Vanguard is a high-performance **Backend API** designed as an autonomous agent to bridge the gap between job seekers and automated recruitment systems. Built with a **Modular MVC / Asynchronous Architecture**, Vanguard acts as a "Digital Twin" to navigate, analyze, and apply for roles via headless browsers.

## 🏗️ Technical Architecture
Developed with **Clean Architecture** and **Asynchronous I/O** at its core:
- **Core Engine:** FastAPI for high-concurrency request handling.
- **Asynchronous Processing:** Leveraging Python's `asyncio` for non-blocking browser interactions and AI reasoning loops powered by **TaskIQ**.
- **Agentic Logic:** A "Reasoning Loop" (Observe -> Think -> Act) powered by **Google Gemini AI** and **Playwright**.
- **Persistence Layer:** PostgreSQL with **Tortoise ORM**, implementing both Pessimistic (`FOR UPDATE`) and Optimistic (`version` column) locking to handle race conditions during task execution.

## 🔐 Security Framework (Zero Trust)
- **Malware Scanning:** Integrated **ClamAV** for scanning uploaded documents before storage.
- **Data Protection:** **AES-256 Encryption** for sensitive portal credentials and JWT for stateless authentication.
- **Isolated Execution:** Sandboxed directory handling for file extractions.

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** Tortoise ORM
* **Task Queue:** TaskIQ
* **Automation:** Playwright
* **AI Integration:** Google Gemini SDK
* **Security:** ClamAV, AES-256

## 📁 Project Structure
``` tree
vanguard-app/
├── core/                       # Shared Engine
│   ├── database.py             # Tortoise Async + Optimistic Lock Config
│   ├── security.py             # AES-256 & PII Masking
│   ├── ai_engine.py            # Gemini SDK + Phoenix Tracing
│   ├── browser.py              # Playwright Worker Setup
│   └── malware_scan.py         # ClamAV Wrapper
├── modules/                    # Business Domains
│   ├── profile/                # M: Portfolio, V: JSON, C: API
│   ├── agent/                  # M: Task, V: JSON, C: API/WS
│   └── generator/              # M: TailoredDoc, V: JSON, C: API
├── shared/                     # The Contract
│   └── schemas.py              # Pydantic (Input/Output Validation)
├── tests/                      # Testing Suite (Pytest)
│   ├── unit/                   # Security, Parsing, & Logic tests
│   ├── integration/            # API Endpoints & DB Race Condition tests
│   ├── e2e/                    # Full Scraping-to-Apply simulations
│   └── conftest.py             # Fixtures for Mock DB & Async Loop
├── main.py                     # App Entry Point
└── .env.example
```
