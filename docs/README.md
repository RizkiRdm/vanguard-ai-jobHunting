# Vanguard Documentation

Welcome to the technical documentation for Vanguard, an AI-powered job hunting assistant that discovers real listings, extracts application materials from your resume, and fills in forms via browser automation while strictly enforcing a human-in-the-loop approval gate.

This documentation is structured according to the **[Diátaxis Framework](https://diataxis.fr/)**, separating information into four distinct quadrants based on user needs:

```
                  PRACTICAL                  THEORETICAL
          ┌─────────────────────────┬─────────────────────────┐
          │                         │                         │
LEARNING  │       Tutorials         │       Explanation       │
ORIENTED  │  (Learning-oriented)    │ (Understanding-oriented)│
          │                         │                         │
          ├─────────────────────────┼─────────────────────────┤
          │                         │                         │
PROBLEM   │      How-To Guides      │        Reference        │
ORIENTED  │   (Problem-oriented)    │ (Information-oriented)  │
          │                         │                         │
          └─────────────────────────┴─────────────────────────┘
```

---

## 1. Tutorials (Learning-Oriented)

_Lessons designed to take a newcomer step-by-step to a complete, successful outcome._

- **[TUTORIAL.md](TUTORIAL.md)**: Zero to First Automated Job Search and Application with Vanguard.
  - Step-by-step walkthrough covering stack startup, user authentication, PDF resume upload with Gemini AI auto-population, DuckDuckGo job discovery, and handling the human-in-the-loop review and approval gate.

---

## 2. How-To Guides (Problem-Oriented)

_Recipes and procedures to solve specific real-world tasks and operational challenges._

- **[SETUP.md](SETUP.md)**: Complete local environment setup guide.
  - Detailed steps for configuring dependencies, environment variables, Supabase credentials, database migrations, and running the three processes.
- **[HOW_TO_GUIDES.md](HOW_TO_GUIDES.md)**: Solutions for common operational and development tasks.
  - How to configure Google OAuth via Supabase Auth.
  - How to review, answer questions, and approve Human-in-the-Loop tasks.
  - How to calibrate daily LLM token spend budgets and API rate limits.
  - How to debug Playwright browser workflows with headless mode turned off.
  - How to author and deploy database migrations safely.
  - How to execute integration tests against a local Postgres instance.

---

## 3. Reference (Information-Oriented)

_Technical specifications, dictionaries, contracts, and schema definitions._

- **[REFERENCE.md](REFERENCE.md)**: Machinery specifications.
  - Bun commands and scripts.
  - Server and web environment variables dictionary.
  - Complete HTTP REST API specification (endpoints, request/response contracts, status codes).
  - Task queue lifecycle states and SQL functions.
- **[FEATURES.md](FEATURES.md)**: Feature mapping table.
  - Maps each user-facing feature across UI routes, server modules, shared contracts, database tables, SQL triggers, and automated tests.
- **[DESIGN.md](DESIGN.md)**: Mobile-first dark UI design system.
  - Design tokens, color palettes, typography, spacing, DaisyUI component patterns, and accessibility guidelines.

---

## 4. Explanation (Understanding-Oriented)

_Architecture, discussions, context, and the "why" behind key system decisions._

- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture and design principles.
  - Deep-dive into Vanguard's three-process model (Web, API, Worker).
  - PostgreSQL task queue concurrency using `SELECT … FOR UPDATE SKIP LOCKED`.
  - Security model: local JWKS token verification, RLS boundaries, private storage buckets, and credential isolation.
  - AI token budgeting and the human-in-the-loop safety guarantee.
- **[AUDIT.md](AUDIT.md)**: Technical audit and legacy Python replacement report.
  - Explains the architectural flaws of the legacy Python prototype and details how the TypeScript migration fixed them.
- **[AGENT_BROWSER_EVALUATION.md](AGENT_BROWSER_EVALUATION.md)**: Evaluation of browser automation engines.
  - Benchmark analysis of Playwright vs `agent-browser` POC.

---

## Quick Navigation

| Document                                  | Type        | Who Should Read It?                                               |
| ----------------------------------------- | ----------- | ----------------------------------------------------------------- |
| [docs/TUTORIAL.md](TUTORIAL.md)           | Tutorial    | New developers or users running Vanguard for the first time       |
| [docs/SETUP.md](SETUP.md)                 | How-To      | Anyone installing and configuring the environment                 |
| [docs/HOW_TO_GUIDES.md](HOW_TO_GUIDES.md) | How-To      | Developers performing specific operations or maintenance          |
| [docs/REFERENCE.md](REFERENCE.md)         | Reference   | Anyone calling APIs, writing queries, or modifying contracts      |
| [docs/FEATURES.md](FEATURES.md)           | Reference   | Developers locating where a specific feature is implemented       |
| [docs/ARCHITECTURE.md](ARCHITECTURE.md)   | Explanation | Anyone seeking to understand the system design and security model |
