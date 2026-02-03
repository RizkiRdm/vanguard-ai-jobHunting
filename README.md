# 🛡️ Vanguard: Autonomous AI Job Hunting Copilot

Vanguard is a high-performance, **Autonomous AI Agent** designed to bridge the gap between job seekers and automated recruitment systems (ATS). Built with a **Modular Monolith Architecture**, Vanguard doesn't just find jobs; it acts as a "Digital Twin" to navigate, analyze, and apply for roles autonomously.

## 🏗️ System Architecture

This project follows **Clean Architecture** principles to ensure long-term scalability and maintainability, making it ready to transition from a personal tool to a multi-user SaaS.

### 🧩 Key Layers:
- **Presentation Layer (Streamlit):** Reactive UI for real-time agent monitoring and profile management.
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

```text
vanguard-app/
├── core/                       # [SYSTEM LAYER] - Internal Engine
│   ├── database.py             # SQLAlchemy Base & Session Engine
│   ├── models_tech.py          # [NEW] Schema: LLMLogs, AgentTasks, PortalHealth
│   ├── llm_client.py           # Unified AI Interface & Token Tracker
│   ├── browser_engine.py       # Playwright Manager (Headless/Headful)
│   └── config.py               # Settings & Secret Management (AES Encryption logic)
├── modules/                    # [BUSINESS LOGIC] - Modular Domains
│   ├── profile/                # Domain: Identity & Skills
│   │   ├── models.py           # Schema: Users, Profiles, Skills, Experiences
│   │   ├── repository.py       # CRUD logic khusus Profile
│   │   └── service.py          # Business Logic: Parsing & Skill Extraction
│   ├── agent/                  # Domain: Autonomous Action
│   │   ├── models.py           # Schema: JobApplications, Portals, Credentials
│   │   ├── planner.py          # Reasoning Loop: Think -> Act -> Observe
│   │   ├── tools.py            # Browser Tools: click(), fill_form()
│   │   └── service.py          # Bridge: Task orchestration
│   ├── generator/              # Domain: Dynamic Content
│   │   ├── service.py          # Logic: AI CV Tailoring
│   │   └── document.py         # Output: PDF/Docx generation
│   └── notifications/          # [NEW] Domain: Engagement
│       ├── models.py           # Schema: User Notifications
│       └── service.py          # Logic: Push/In-app alerts
├── shared/                     # [CONTRACT LAYER] - Data Bridge
│   └── schemas.py              # Pydantic Models (The "Source of Truth" for AI)
├── ui/                         # [PRESENTATION LAYER] - Streamlit
│   ├── components/             # Reusable UI (Log Terminal, Metric Cards)
│   └── pages/                  # Streamlit Multi-page Routing
├── data/                       # Local Storage (DuckDB DB, Screenshots)
├── main.py                     # Entry Point
└── requirements.txt
```

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Backend Framework:** FastAPI / Streamlit (Interface)
* **ORM:** SQLAlchemy 2.0
* **Automation:** Playwright
* **AI Integration:** OpenAI API / Anthropic / LangChain
* **Validation:** Pydantic v2

## 🚀 Future Roadmap

* [ ] **Multi-user SaaS Support:** Integrated Auth & Subscription management.
* [ ] **IP Rotation:** Proxy integration for high-volume job scouting.
* [ ] **Advanced Human-in-the-loop:** Mobile notifications for final submission approval.

---

>*Developed with a focus on Scalability, Security, and Efficiency.*