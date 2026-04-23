## 🏗️ Vanguard: Master Production-Ready Todo List

### 🚩 Milestone 1: Foundation & Secure Infrastructure

**Outcome:** Sistem dasar dapat berkomunikasi dengan DB dan mengenkripsi data sensitif.

* [ x] **VG-1.1: Environment & Async Database Handshake**
* **Type:** Core | **Layer:** Infra/DB
* **Task:** Setup `Tortoise ORM`.
* **DoD:** `pytest tests/unit/test_db_connection.py` pass 100%. Alembic `head` tercapai.


* [ x] **VG-1.2: AES-256 Cryptographic Vault**
* **Type:** Core | **Layer:** Security/Shared
* **Task:** Implementasi modul enkripsi di `core/security.py`. Wajib menggunakan `Fernet` (cryptography) dengan rotasi key via `.env`.
* **DoD:** Test case "Roundtrip" (Encrypt -> Decrypt == Original) dan "Wrong Key Exception" lulus.


* [ x] **VG-1.3: Profile Schema & PII Masking**
* **Type:** Core | **Layer:** DB/API
* **Task:** Implementasi Model `User` dan `Profile`. Tambahkan logic `mask_email()` dan `mask_phone()` pada level Schema.
* **DoD:** API `/profile` mengembalikan data dengan PII ter-masking sesuai role.



---

### 🤖 Milestone 2: Agent Reasoning & Automation Engine

**Outcome:** Worker dapat menjalankan instruksi navigasi browser yang dipandu oleh AI.

* [ x] **VG-2.1: Playwright Async Worker Scaffolding**
* **Type:** Core | **Layer:** Infra/Worker
* **Task:** Setup `core/browser.py`. Implementasi `browser_context` yang melakukan *auto-close* dan *screenshot on failure*.
* **DoD:** Worker berhasil mengambil screenshot dari URL dummy tanpa memory leak.


* [ x] **VG-2.2: Gemini AI Reasoning Loop**
* **Type:** Core | **Layer:** AI/Module
* **Task:** Integrasi SDK Gemini di `modules/agent/ai_engine.py`. Implementasi prompt untuk konversi HTML DOM ke JSON Action (FILL, CLICK, WAIT).
* **DoD:** Unit test dengan *mock response* Gemini menghasilkan JSON action yang valid sesuai `shared/schemas.py`.


* [ x] **VG-2.3: Task State Machine & Concurrency Control**
* **Type:** Core | **Layer:** Backend/DB
* **Task:** Implementasi `FOR UPDATE` lock saat worker mengambil task. Update status: `QUEUED` -> `RUNNING` -> `COMPLETED/FAILED`.
* **DoD:** Menjalankan 2 worker secara konkuren tidak menyebabkan *double-processing* pada task yang sama.



---

# 🛡️ MILESTONE 3 — Security Hardening & Malware Shield

Outcome: Sistem tahan file jahat & abuse API.

---

## [x] VG-3.1 — ClamAV Malware Scanning Pipeline

Type: Core
Layer: Security/Infra

### 1️⃣ Context Lock

* Python 3.12
* FastAPI
* Upload menggunakan `UploadFile`
* ClamAV daemon aktif via `clamd`
* File hanya ZIP
* Upload endpoint sudah ada di `modules/generator`
* Wrapper lokasi: `core/malware_scan.py`
* Server running clamd via TCP (127.0.0.1:3310)

### 2️⃣ Contract

* Setiap file ZIP harus discan sebelum parsing/generator dijalankan.
* Jika terdeteksi malware → raise HTTPException 403.
* Jika clean → lanjut ke pipeline.
* Scan dilakukan secara streaming (tidak simpan permanen dulu).

### 3️⃣ Implementation Constraints

* Gunakan `clamd.ClamdNetworkSocket`
* Tidak boleh blocking I/O
* Tidak boleh load file full ke memory jika > 10MB
* Error koneksi ClamAV → fail closed (reject upload)
* Logging wajib structured JSON (structlog nanti)

### 4️⃣ Integration Points

* Dipanggil di endpoint:
  modules/generator/controller sebelum AI parsing
* Fungsi publik:
  `async def scan_upload(file: UploadFile) -> None`

### 5️⃣ Verification Scenario

Scenario A – Clean File:

* Upload ZIP biasa
  Expected:
* HTTP 200
* Generator dipanggil

Scenario B – EICAR:

* Upload file EICAR test string
  Expected:
* HTTP 403
* Error message: “Malicious file detected”
* Generator tidak dieksekusi

---

## [x] VG-3.2 — Rate Limiting & JWT Implementation

Type: Core
Layer: Security/API

### 1 Context Lock

* FastAPI
* Auth via `python-jose`
* Password hashing via `passlib`
* Cookie-based JWT (httpOnly, secure=True, samesite=lax)
* Endpoint sensitif: `/agent/scrape`

### 2 Contract

* Endpoint sensitif dibatasi 10 request / menit per IP
* JWT disimpan dalam httpOnly cookie
* Token expiry default 15 menit
* Refresh token optional (tidak mandatory sekarang)

### 3 Implementation Constraints

* Tidak boleh pakai header Authorization
* JWT tidak boleh di localStorage
* Rate limit global memory store cukup (no Redis)
* Middleware tidak boleh blocking
* Error:

  * 401 → invalid/expired token
  * 429 → rate limit exceeded

### 4 Integration Points

* JWT logic di `core/security.py`
* Rate limiter applied di `main.py`
* Protected router di `modules/agent`

### 5 Verification Scenario

Scenario A – No JWT:

* Hit protected endpoint
  Expected: HTTP 401

Scenario B – Valid JWT:

* Hit <10 times per minute
  Expected: HTTP 200

Scenario C – Abuse:

* Hit >10 times per minute
  Expected: HTTP 429

---

# 📈 MILESTONE 4 — Observability & Production Readiness

## [x] VG-4.1 — Structured Logging & Token Audit

Type: Technical Debt
Layer: Monitoring

### 1 Context Lock

* Logging library: `structlog`
* Output: JSON
* LLM provider: Gemini SDK
* DB: PostgreSQL via Tortoise
* Table: llm_usage_logs

### 2 Contract

* Semua log output dalam JSON
* Setiap call Gemini harus simpan:

  * prompt_tokens
  * completion_tokens
  * total_tokens
  * user_id (nullable)
  * timestamp
* Tidak boleh blocking DB insert

### 3  Implementation Constraints

* structlog processor chain wajib include:

  * timestamp
  * log level
  * event
* Tidak boleh pakai print()
* Insert token log via async session

### 4 Integration Points

* Hook di `core/ai_engine.py`
* DB model di modules/agent atau shared models

### 5 Verification Scenario

Scenario:

* Trigger 1 AI request
  Expected:
* Log stdout dalam JSON valid
* 1 row masuk llm_usage_logs
* Format readable oleh ELK / CloudWatch

---

## [x] VG-4.2 — Automated E2E Regression

Type: Core
Layer: Testing

### 1 Context Lock

* pytest
* pytest-asyncio
* Playwright
* CI target: GitHub Actions
* DB test via isolated container

### 2 Contract

E2E flow:

Upload ZIP → Malware Scan → AI Parse → Create Task → Browser Apply

Semua lulus tanpa error.

### 3 Implementation Constraints

* Tidak boleh hit external Gemini (mock response)
* Tidak boleh hit real Playwright browser (headless mock)
* Test harus bisa jalan < 60 detik

### 4 Integration Points

* tests/e2e/test_full_pipeline.py
* Fixtures di conftest.py

### 5 Verification Scenario

CI Run:

* pytest exits 0
* No network calls ke external API
* Coverage > 80%

---

## [x] VG-4.3 — Swagger API Documentation

Type: Core
Layer: Documentation

### 1 Context Lock

* FastAPI auto OpenAPI
* Semua schema via shared/schemas.py
* Custom error response models

### 2 Contract

* Semua endpoint memiliki:

  * request model
  * response model
  * error response model
* `/docs` dan `/openapi.json` aktif

### 3 Implementation Constraints

* Tidak boleh return dict mentah
* Semua response via Pydantic model
* Error harus consistent schema

### 4 Integration Points

* main.py
* shared/schemas.py

### 5 Verification Scenario

Manual:

* Akses /docs
  Expected:
* Semua endpoint muncul
* Bisa test via UI
* Error response terdokumentasi

---

# 🚦 Production Deployment Criteria (Upgraded)

Ubah jadi executable checklist.

## PDC Spec

1. Security Scan

   * bandit -r .
   * safety check
     Expected: No HIGH severity

2. Coverage

   * pytest --cov
     Expected: >= 80%

3. Env Isolation

   * .env.production tidak boleh di-commit
   * ENV=production tidak load dev config

4. Async Safety
   Static scan:

   * Tidak ada time.sleep
   * Tidak ada requests.get
   * Tidak ada psycopg2 sync call