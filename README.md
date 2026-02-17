# 🛡️ Vanguard: Autonomous AI Job Hunting Copilot

Vanguard is a high-performance, **Autonomous AI Agent** designed to bridge the gap between job seekers and automated recruitment systems (ATS). Built with a **Modular Monolith Architecture**, Vanguard doesn't just find jobs; it acts as a "Digital Twin" to navigate, analyze, and apply for roles autonomously.

## 🏗️ System Architecture

This project follows **Clean Architecture** principles to ensure long-term scalability and maintainability, making it ready to transition from a personal tool to a multi-user SaaS.

### 🧩 Key Layers:
- **Agentic Layer (Playwright + LLM):** An autonomous "Reasoning Loop" (Observe -> Think -> Act) that controls a headless browser.
- **Service/Business Layer:** Encapsulated logic for resume tailoring, skill extraction, and job matching.
- **Data Access Layer (SQLAlchemy):** Decoupled repository pattern supporting 3NF normalized schemas for business data.
- **Technical/Audit Layer:** Dedicated logging for LLM token usage, execution trails, and system health monitoring.

## 🗄️ Database Design (3NF)

The system utilizes two distinct logical schemas:
1. **Business Schema:** High normalization (3rd Normal Form) for `Users`, `Profiles`, `Experiences`, and `Skills` to ensure data integrity and query performance.
2. **Technical Schema:** Optimized for high-write throughput (1NF/2NF) to handle `Agent_Tasks`, `LLM_Usage_Logs`, and `Execution_Audit_Trails`.

## 🤖 Agentic Workflow (LLAD)

Vanguard's agent operates using **Tiered Intelligence**:
- **Scanning (Fast/Cheap):** GPT-4o-mini analyzes DOM structures and performs basic navigation.
- **Decision Making (Reasoning):** Claude 3.5 / GPT-4o evaluates job relevancy and crafts tailored application responses.
- **Action (Playwright):** Human-like interactions (delays, mouse movement) to minimize bot detection.

## 📁 Project Structure

``` tree
vanguard-app/
├── core/                       # Shared Engine
│   ├── database.py             # SQLAlchemy Async + Optimistic Lock Config
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

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Backend Framework:** FastAPI
* **Documentation:** Scalar
* **ORM:** SQLAlchemy 2.0
* **Async Task Queue:** TaskIQ
* **Malware Scanning:** ClamAV
* **AI Observability:** Arize Phoenix
* **Automation:** Playwright
* **Database:** PostgreSQL
* **AI Integration:** Gemini AI SDK
* **Validation:** Pydantic v2
* **Security:** AES-256, JWT, OAuth

## 🚀 Future Roadmap

* [ ] **IP Rotation:** Proxy integration for high-volume job scouting.
* [ ] **Advanced Human-in-the-loop:** Mobile notifications for final submission approval.

---

>*Developed with a focus on Scalability, Security, and Efficiency.*