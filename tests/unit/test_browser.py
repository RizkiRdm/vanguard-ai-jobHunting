import pytest
import os
import glob
from core.browser import BrowserManager


@pytest.mark.asyncio
async def test_browser_context_management():
    """Ensuring that the browser can open/close without errors (Resource Test)."""
    manager = BrowserManager(headless=True)
    title = await manager.simple_navigate("https://example.com", "test_res")
    assert "Example Domain" in title


@pytest.mark.asyncio
async def test_browser_failure_triggers_screenshot():
    """
    DoD: Workers must take a screenshot when an error occurs (Invalid URL).
    """
    manager = BrowserManager(headless=True)
    invalid_url = "https://this-domain-does-not-exist-12345.com"
    task_id = "test_failure_logic"

    # Kita sengaja buat gagal
    with pytest.raises(Exception):
        await manager.simple_navigate(invalid_url, task_id)

    # Verification of the generated screenshot file
    files = glob.glob(f"storage/screenshots/FAIL_{task_id}_*.png")
    assert len(files) > 0, "Screenshot failure not found!"

    # Clean up test files so they don't pile up
    for f in files:
        os.remove(f)
    print(f"\n✅ SUCCESS: Screenshot verified for task {task_id}")
