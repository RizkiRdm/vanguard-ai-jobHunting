import pytest
import os
import glob
from core.browser import BrowserManager


@pytest.mark.asyncio
async def test_browser_context_management():
    """Ensuring that the browser can open/close without errors (Resource Test)."""
    manager = BrowserManager()
    await manager.connect()
    try:
        res = await manager.open_url("https://example.com")
        assert res is not None
    finally:
        await manager.disconnect()


@pytest.mark.asyncio
async def test_browser_failure_triggers_screenshot():
    """
    DoD: Workers must take a screenshot when an error occurs (Invalid URL).
    """
    manager = BrowserManager()
    await manager.connect()
    try:
        invalid_url = "https://this-domain-does-not-exist-12345.com"
        task_id = "test_failure_logic"

        # Kita sengaja buat gagal dengan open_url ke domain invalid
        with pytest.raises(Exception):
            await manager.open_url(invalid_url)
            await manager.take_screenshot(f"FAIL_{task_id}")

        # Verification of the generated screenshot file
        files = glob.glob(f"storage/screenshots/FAIL_{task_id}.png")
        assert len(files) > 0, "Screenshot failure not found!"

        # Clean up test files so they don't pile up
        for f in files:
            os.remove(f)
    finally:
        await manager.disconnect()
