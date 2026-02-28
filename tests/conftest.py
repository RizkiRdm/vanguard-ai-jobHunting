import asyncio
import json
import os
import pytest
from tortoise import Tortoise
from dotenv import load_dotenv
from unittest.mock import patch, AsyncMock, MagicMock
from tortoise.contrib.test import finalizer

load_dotenv()


@pytest.fixture(scope="session")
def event_loop():
    """
    Memastikan satu event loop yang konsisten digunakan selama seluruh sesi test.
    Ini mencegah asyncpg 'nyangkut' di loop yang berbeda.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def db_setup():
    """
    Setup database yang lebih bersih dengan pembersihan total sebelum & sesudah test.
    """
    db_url = os.getenv("DATABASE_URL")

    # Tambahkan parameter pool agar lebih stabil di environment testing
    if "?" in db_url:
        db_url = f"{db_url}&minsize=1&maxsize=5"
    else:
        db_url = f"{db_url}?minsize=1&maxsize=5"

    # 1. Pastikan state Tortoise benar-benar bersih sebelum mulai
    # Menggunakan hasattr untuk mencegah error jika Tortoise belum init
    if hasattr(Tortoise, "_connections"):
        await Tortoise.close_connections()
    Tortoise.apps = {}
    Tortoise._connections = {}

    # 2. Inisialisasi koneksi baru
    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": [
                "modules.agent.models",
                "modules.profile.models",
                "modules.generator.models",
            ]
        },
    )

    # 3. Generate Schema (Gunakan safe mode agar tidak error jika tabel sudah ada)
    await Tortoise.generate_schemas(safe=True)

    yield

    # 4. Cleanup Final: Tutup semua koneksi sebelum loop berganti
    await Tortoise.close_connections()


@pytest.fixture(autouse=True)
def mock_pipeline_dependencies():
    """Bypass all external network calls for E2E tests"""
    with patch("core.security.httpx.AsyncClient.get") as mock_vt:
        mock_vt.return_value = MagicMock(status_code=404)

        with patch("google.genai.Client") as mock_client:
            mock_instance = mock_client.return_value
            mock_resp = MagicMock()

            # This JSON must match what test_scraping.py expects
            mock_resp.text = json.dumps(
                {
                    "job_title": "AI Architect",
                    "company_name": "Mock Corp",
                    "location": "Remote",
                    "employment_type": "Full-time",
                    "salary_range": "100k",
                    "job_description": "Testing",
                    "requirements": ["Python"],
                    "source_url": "https://example.com",
                    "posted_date": "Today",
                }
            )
            mock_resp.usage_metadata.prompt_token_count = 10
            mock_resp.usage_metadata.candidates_token_count = 10
            mock_resp.usage_metadata.total_token_count = 20

            mock_instance.models.generate_content = AsyncMock(return_value=mock_resp)

            # Mock Playwright Context Manager
            mock_page = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value="Mocked Page Content")
            mock_page.goto = AsyncMock()

            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock(return_value=mock_page)

            with patch("core.browser.BrowserManager.get_context") as mock_get_ctx:
                mock_get_ctx.return_value.__aenter__.return_value = mock_context
                yield


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


@pytest.fixture(autouse=True)
def mock_browser_context():
    """Mocking Playwright Context Manager & Page behavior"""
    # 1. Buat Mock untuk Page
    mock_page = AsyncMock()
    mock_page.url = "https://mock-job-site.com/listing"
    mock_page.goto = AsyncMock()
    mock_page.evaluate = AsyncMock(return_value="Fake Page Content for AI")
    mock_page.inner_text = AsyncMock(return_value="Mocked Text")

    # 2. Buat Mock untuk Context
    mock_context = AsyncMock()
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_context.close = AsyncMock()

    # 3. Patch get_context sebagai Async Context Manager
    # __aenter__ akan mengembalikan mock_context
    with patch("core.browser.BrowserManager.get_context") as mock_get_context:
        mock_get_context.return_value.__aenter__.return_value = mock_context
        yield mock_page
