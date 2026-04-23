# Dev Log: Vanguard AI

2026-03-19

- **Audit Awal**: Mengidentifikasi risiko _token leakage_ dan instabilitas Tortoise ORM.
- **Refactor Core AI**: Menambahkan `check_budget_limit` pada `ai_agent.py`.

2026-03-20

- **Pivot Strategi**: Mengganti modul scraper menjadi Google Dorking di `scraper.py`.
- **Implementasi WebSocket**: Membuat `ConnectionManager` di backend.

2026-03-21 (Today)

- **Frontend Initialization**: Setup React Vite dengan TypeScript.
- **Profile Service Implementation**: Pembuatan `profile_router.py` dan `useProfileStore.ts` untuk manajemen data kandidat.
- **Dynamic Orchestration**: Integrasi path resume dinamis ke dalam `JobOrchestrator` agar bot bisa menggunakan file yang diunggah user.
- **WebSocket Hook Implementation**:
  - Membuat `useAgentSocket.ts` untuk menangani koneksi real-time.
  - Implementasi logika _auto-reconnect_ (3 detik) untuk stabilitas monitoring.
- **UI Framework Pivot**:
  - Melakukan migrasi penuh ke **TailAdmin Dashboard** untuk menghindari _UI bug_ saat _copy-paste_ komponen manual.
  - Mengintegrasikan logic Zustand dan WebSocket ke dalam `App.tsx` dan `DefaultLayout` TailAdmin.
- **Root Orchestration**: Mengonfigurasi `App.tsx` sebagai pusat kendali yang menjalankan `fetchProfile` dan inisialisasi socket secara global.
- **Decision Log**: Memutuskan untuk tetap menggunakan **Native WebSocket** daripada Socket.io guna meminimalisir overhead dan menjaga konsistensi arsitektur backend FastAPI.
