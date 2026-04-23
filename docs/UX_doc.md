### 1. Ide Gambaran UI/UX: Hybrid Command Center
User memiliki satu halaman utama (Dashboard) untuk memantau performa bot, dan sebuah panel interaksi di sisi kanan untuk berkomunikasi dengan AI.

* **Bentuk:** Dashboard Sidebar dengan Floating Action Button (FAB) untuk membuka "Agent Thought Stream".
* **Kenapa:** User butuh transparansi. Mereka ingin melihat screenshot terakhir (`/agent/tasks/{id}/screenshot`) untuk memastikan bot tidak melakukan kesalahan.

---

### 2. ASCII Wireframe

#### A. Main Dashboard (Job List & Stats)
Endpoint: `/profile/stats`, `/agent/tasks`, `/profile/me`

```text
_________________________________________________________________________
| [VANGUARD AI] | Welcome, user@email.com [Logout]                      |
|_______________|_______________________________________________________|
|               |                                                       |
|  ( ) Summary  |  [ ACTIVE RESUME ]          [ BOT STATISTICS ]        |
|  ( ) Jobs     |  File: MyCV_2024.pdf        Applied: 142              |
|  ( ) Profile  |  [ Change Resume ]          Token cost: 45k           |
|  ( ) Settings |_______________________________________________________|
|               |                                                       |
|_______________|  [ CURRENT TASKS ]                                    |
|               |  ID       | TYPE      | STATUS      | ACTION          |
| [!] Agent is  |  8821...  | APPLY     | RUNNING     | [View Stream]   |
|     Active    |  712a...  | DISCOVERY | COMPLETED   | [View Jobs]     |
|_______________|_______________________________________________________|
```

#### B. Agent Interaction Panel (The ReAct Stream)
Endpoint: `/agent/tasks/{id}`, `/agent/tasks/{id}/screenshot`, `/agent/interact/{id}`

```text
__________________________________________________________
| [X] AGENT STREAM - Task #8821                          |
|________________________________________________________|
| [Thought]: I am clicking the "Easy Apply" button.      |
| [Action ]: CLICK on button.job-apply-primary           |
|                                                        |
|  ____________________________________________________  |
| |                                                    | |
| |        [ IMAGE: LATEST_SCREENSHOT.JPG ]            | |
| |____________________________________________________| |
|                                                        |
| [!] AGENT NEEDS HELP:                                  |
| "What is your notice period?"                          |
| [__________________________________________] [Send]    |
|________________________________________________________|
```

---

### 3. Dokumen UX (User Flow)

**Flow 1: Onboarding & Setup**
1.  **Login/Register:** User masuk via `/profile/auth/google`.
2.  **Upload Resume:** User mengunggah CV di `/profile/upload-resume`. Frontend memanggil endpoint ini dan secara otomatis mentrigger task `DISCOVERY` (sesuai logic di router kita).
3.  **Status Check:** Dashboard melakukan polling ke `/agent/tasks` untuk menampilkan progress bar.

**Flow 2: Human-in-the-Loop (HITL)**
1.  **Notification:** Bot menemui pertanyaan sulit dan mengubah status task menjadi `AWAITING_USER`.
2.  **Interaction:** Frontend mendeteksi status ini, membuka *Agent Stream Panel*, dan menampilkan `subjective_question` dari metadata task.
3.  **Resume Task:** User mengetik jawaban, frontend mengirim `POST /agent/interact/{id}`, dan status task kembali ke `QUEUED` untuk dilanjutkan oleh worker.

**Flow 3: Monitoring & Debugging**
1.  **Visual Proof:** User penasaran kenapa bot berhenti. User klik "View Screenshot".
2.  **API Call:** Frontend memanggil `GET /agent/tasks/{id}/screenshot` dan menampilkannya di modal.

---

### 4. Konfirmasi Pemanfaatan API (Tanpa API Baru)

Desain di atas **100% menggunakan API yang sudah kita buat**:

1.  **Statistik di Header:** Memanfaatkan `/profile/stats` yang mengagregasi data dari `LLMUsageLog` dan `AgentTask`.
2.  **Identitas:** Memanfaatkan `/profile/me` untuk menampilkan email dan provider (Google/Local).
3.  **Pengiriman Jawaban:** Memanfaatkan `/agent/interact/{task_id}`. Kita asumsikan frontend mengirim JSON `{"answer": "30 days"}` yang akan disimpan ke `metadata["human_answer"]`.
4.  **Monitoring AI:** Memanfaatkan `metadata["thought"]` dan `metadata["action"]` yang dihasilkan oleh `VanguardAI` di `orchestrator.py` dan disimpan ke dalam model `AgentTask`.
5.  **Rate Limit Info:** Jika user melakukan spam, frontend menangkap error `429` dari middleware `main.py` dan menampilkan pesan: *"Too many requests. Please wait 60s."*