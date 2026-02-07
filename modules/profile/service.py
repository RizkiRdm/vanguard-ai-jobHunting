import json
import os
import httpx
import asyncio
from typing import Dict, Any
from uuid import UUID
from datetime import datetime
from modules.profile.models import UserExperience
from modules.profile.repository import ProfileRepository
from core.database import AsyncSessionLocal
from pathlib import Path
from dotenv import load_dotenv
from google import genai


load_dotenv()
CV_PARSER_SYSTEM_PROMPT = Path("docs/SYSTEM_PROMPT.md").read_text(encoding="utf-8")


class ProfileService:
    """
    Service layer for Profile operations, including AI-powered CV parsing.
    Uses the official google-genai SDK for seamless integration.
    """

    def __init__(self, repository: ProfileRepository):
        self.repo = repository
        # Client secara otomatis mengambil GEMINI_API_KEY dari environment variable
        self.client = genai.Client()
        self.model_id = "gemini-2.0-flash"

    async def parse_cv_with_ai(self, user_id: UUID, cv_text: str) -> Dict[str, Any]:
        """
        Mengirim teks CV ke Gemini menggunakan library google-genai.
        """

        # Konfigurasi generate content
        config = {
            "system_instruction": CV_PARSER_SYSTEM_PROMPT,
            "generation_config": {
                "response_mime_type": "application/json",
            },
        }

        # Implementasi Exponential Backoff untuk menangani rate limit atau gangguan koneksi
        for attempt in range(5):
            try:
                response = self.client.models.generate_content(
                    model=self.model_id,
                    contents=f"CV Text to parse:\n{cv_text}",
                    config=config,
                )

                # Mengambil output teks (yang sudah dipastikan berupa JSON oleh config)
                parsed_data = json.loads(response.text)

                # Memproses dan menyimpan hasil ke database
                return await self._save_ai_results(user_id, parsed_data)

            except Exception as e:
                if attempt == 4:
                    raise RuntimeError(f"AI Parsing failed after 5 attempts: {str(e)}")
                # Jeda progresif: 1s, 2s, 4s, 8s
                await asyncio.sleep(2**attempt)

    async def _save_ai_results(
        self, user_id: UUID, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Memetakan output JSON AI ke Model Database melalui Repository.
        """
        # 1. Update Header Profil
        profile = await self.repo.create_or_update_profile(
            user_id=user_id,
            summary=data.get("summary"),
            target_role=data.get("target_role"),
            last_parsed_at=datetime.utcnow(),
        )

        # 2. Sinkronisasi Pengalaman Kerja
        # Membersihkan data lama sebelum memasukkan hasil parsing terbaru
        from sqlalchemy import delete

        await self.repo.db.execute(
            delete(UserExperience).where(UserExperience.profile_id == profile.id)
        )

        for exp in data.get("experiences", []):
            await self.repo.add_experience(profile.id, **exp)

        # 3. Sinkronisasi Skills
        await self.repo.sync_skills(profile.id, data.get("skills", []))

        # Commit semua perubahan dalam satu transaksi
        await self.repo.commit()

        return {
            "status": "success",
            "profile_id": str(profile.id),
            "message": "CV successfully parsed and profile updated.",
        }
