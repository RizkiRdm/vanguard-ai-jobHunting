import os
import uuid
import pytest
from PIL import Image
from core.ai_agent import VanguardAI
from core.custom_logging import setup_logging
from modules.agent.models import AgentLLMUsageLog as LLMUsageLog
from modules.profile.models import User


@pytest.mark.asyncio
async def test_structured_logging_and_token_audit(capsys):
    # --- 1. SETUP ---
    setup_logging()
    test_user = await User.create(
        email=f"test_{uuid.uuid4()}@example.com",
    )
    user_test_id = test_user.id

    mock_file = "test_screen.png"

    # KUNCI: Buat file gambar DULU sebelum agent jalan
    img = Image.new("RGB", (100, 100), color="blue")
    img.save(mock_file)

    # Bersihkan DB agar state bersih
    await LLMUsageLog.all().delete()

    try:
        # --- 2. EXECUTION ---
        agent = VanguardAI()

        # Karena di ai_agent.py kita sudah pakai 'await' untuk logging,
        # baris ini baru akan kelar SETELAH data masuk ke database.
        await agent.analyze_screen(
            mock_file, "Find submit button", user_id=user_test_id
        )

        # --- 3. ASSERTION DATABASE ---
        # Langsung cek DB, tidak perlu sleep karena prosesnya sudah sinkron (await)
        log_entry = await LLMUsageLog.filter(user_id=user_test_id).first()

        assert log_entry is not None, (
            f"Database record missing for user_id: {user_test_id}"
        )
        assert log_entry.total_tokens == 150
        assert log_entry.model_name == "gemini-1.5-flash"

        # --- 4. ASSERTION LOGGING (STDOUT) ---
        captured = capsys.readouterr()
        assert "ai_analysis_started" in captured.out
        assert "token_audit_saved" in captured.out
        assert str(user_test_id) in captured.out

    finally:
        # --- 5. CLEANUP ---
        # Hapus file sampah agar tidak mengotori repository
        if os.path.exists(mock_file):
            os.remove(mock_file)
