import os
import pytest
from tortoise import Tortoise
from dotenv import load_dotenv
from unittest.mock import patch, AsyncMock, MagicMock

load_dotenv()


@pytest.fixture(autouse=True)
async def db_setup():
    db_url = os.getenv("DATABASE_URL")

    # Tambahkan parameter pool langsung ke DSN
    pool_params = "minsize=2&maxsize=20"
    if "?" in db_url:
        db_url = f"{db_url}&{pool_params}"
    else:
        db_url = f"{db_url}?{pool_params}"

    # Reset state Tortoise dengan benar (await coroutine)
    await Tortoise._reset_apps()

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["modules.agent.models", "modules.profile.models"]},
    )
    await Tortoise.generate_schemas()

    yield

    await Tortoise.close_connections()


@pytest.fixture(autouse=True)
def mock_pipeline_dependencies():
    """Bypass semua external network calls untuk E2E test"""

    # 1. Mock Malware Scanner (VirusTotal)
    with patch("core.security.httpx.AsyncClient.get") as mock_vt:
        # Simulasikan file bersih
        mock_vt.return_value = MagicMock(status_code=404)

        # 2. Mock Gemini API (google.genai)
        with patch("google.genai.Client") as mock_genai:
            client_inst = mock_genai.return_value
            mock_res = MagicMock()
            mock_res.text = '{"action": "complete", "reasoning": "all fields filled"}'
            mock_res.usage_metadata.prompt_token_count = 100
            mock_res.usage_metadata.candidates_token_count = 50
            mock_res.usage_metadata.total_token_count = 150

            client_inst.models.generate_content = AsyncMock(return_value=mock_res)

            # 3. Mock Playwright (Browser)
            with patch("playwright.async_api.async_playwright") as mock_pw:
                pw_inst = AsyncMock()
                browser = AsyncMock()
                page = AsyncMock()

                mock_pw.return_value.__aenter__.return_value = pw_inst
                pw_inst.chromium.launch.return_value = browser
                browser.new_context.return_value.__aenter__.return_value = AsyncMock()
                # Kita arahkan agar get_context() mengembalikan mock page

                yield {"gemini": client_inst.models.generate_content, "vt": mock_vt}


@pytest.fixture(autouse=True)
def mock_external_calls():
    """Global mock untuk mencegah network call selama E2E test"""

    # 1. Mock Gemini SDK
    with patch("google.genai.Client") as mock_genai:
        client_instance = mock_genai.return_value
        mock_response = MagicMock()
        mock_response.text = '{"action": "complete", "reasoning": "form filled"}'
        mock_response.usage_metadata.prompt_token_count = 100
        mock_response.usage_metadata.candidates_token_count = 50
        mock_response.usage_metadata.total_token_count = 150

        client_instance.models.generate_content = AsyncMock(return_value=mock_response)

        # 2. Mock Malware Scan (Httpx call inside MalwareScanner)
        with patch("httpx.AsyncClient.get") as mock_vt:
            mock_vt.return_value = MagicMock(status_code=404)  # Simulate clean file

            # 3. Mock Playwright
            with patch("playwright.async_api.async_playwright") as mock_pw:
                yield {
                    "gemini": client_instance.models.generate_content,
                    "playwright": mock_pw,
                }
