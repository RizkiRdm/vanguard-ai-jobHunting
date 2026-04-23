**Last Updated**: 2026-03-21

## Completed

- **Setup**: Struktur proyek backend menggunakan FastAPI dan Tortoise ORM.
- **Core AI Integration**: Implementasi `VanguardAI` menggunakan Google GenAI SDK (Gemini 2.0 Flash).
- **Autonomous Engine**: Implementasi ReAct loop di `JobOrchestrator` untuk navigasi browser mandiri.
- **Dynamic Resume Integration**: `JobOrchestrator` kini secara dinamis mengambil `resume_url` dari `UserProfile` untuk proses unggah otomatis.
- **Cost Control**: Mekanisme `check_budget_limit` untuk membatasi penggunaan token harian.
- **Dorking Logic**: Transisi ke Google Dorking untuk mencari halaman karir secara langsung.
- **Real-time Streaming**: Implementasi `ConnectionManager` (WebSocket) backend dan `useAgentSocket` hook di frontend.
- **Frontend Framework Migration**: Migrasi penuh ke **TailAdmin Dashboard** (React + Tailwind) sebagai basis UI utama untuk mempercepat development.
- **Global State Management**: Implementasi Zustand (`useAgentStore`, `useProfileStore`) terintegrasi dengan layout dashboard.
- **User Profile System**: Backend router untuk manajemen kandidat dan fitur unggah resume telah sinkron dengan interface frontend.

## In Progress

- **Dashboard Integration**: Menghubungkan komponen visual TailAdmin (Charts & Tables) dengan data real-time dari bot.
- **Human-in-the-Loop (HITL)**: Finalisasi alur `AWAIT_USER` untuk menangani pertanyaan kompleks via UI.
- **WebSocket Auth**: Pengamanan koneksi WebSocket menggunakan JWT _handshake_.

## Not Started

- **Live Screenshot Monitor**: Pengembangan panel khusus untuk menampilkan streaming gambar dari browser bot.
- **Resume Tailoring**: Integrasi AI untuk modifikasi CV secara otomatis sesuai deskripsi pekerjaan.

## Architecture Snapshot

- **Backend**: FastAPI (Async) dengan Playwright.
- **AI Engine**: Gemini 2.0 Flash (Multimodal).
- **Database**: Tortoise ORM (PostgreSQL).
- **Frontend**: React (TailAdmin Template) + Vite + TypeScript.
- **Communication**: Native WebSocket untuk _real-time agent streaming_ (Keputusan: Menunda penggunaan Socket.io).
