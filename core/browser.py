import random
import asyncio
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright, Page, BrowserContext, Browser


class BrowserManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.session_dir = Path("storage/sessions")
        self.screenshot_dir = Path("storage/screenshots")

        # Ensure directories exist
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    async def _stealth_js(self, page: Page):
        """Injects advanced JavaScript to bypass basic automation detection."""
        await page.add_init_script(
            """
            // Overwrite the transparency of the webdriver property
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Mock languages and plugins
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

            // Fix for Chrome-based detection
            window.chrome = { runtime: {} };
        """
        )

    async def load_session_state(self, user_id: str) -> Optional[str]:
        """Checks if a session file exists for the user and returns the path."""
        session_file = self.session_dir / f"{user_id}.json"
        if session_file.exists():
            return str(session_file)
        return None

    async def save_session_state(self, context: BrowserContext, user_id: str):
        """Persists the current browser cookies and local storage to disk."""
        try:
            session_file = self.session_dir / f"{user_id}.json"
            await context.storage_state(path=str(session_file))
        except Exception as e:
            print(f"[BROWSER] Failed to save session for {user_id}: {e}")

    @asynccontextmanager
    async def get_context(self, user_id: str = None, load_session: bool = True):
        """
        Creates a stateful browser context.
        If user_id is provided, it attempts to load/save session cookies.
        """
        async with async_playwright() as p:
            # High-level launch arguments for stability and stealth
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )

            # Randomize dynamic fingerprints
            width = random.randint(1280, 1440)
            height = random.randint(800, 900)

            context_kwargs = {
                "viewport": {"width": width, "height": height},
                "user_agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(110, 122)}.0.0.0 Safari/537.36",
                "locale": "en-US",
                "timezone_id": "Asia/Jakarta",
            }

            # Load existing session if available
            if user_id and load_session:
                session_path = await self.load_session_state(user_id)
                if session_path:
                    context_kwargs["storage_state"] = session_path

            context = await browser.new_context(**context_kwargs)

            try:
                yield context
            finally:
                # Critical: Save session state before closing
                if user_id:
                    await self.save_session_state(context, user_id)

                await context.close()
                await browser.close()

    async def human_type(self, page: Page, selector: str, text: str):
        """Types text with variable delays and occasional 'human' mistakes."""
        await page.wait_for_selector(selector, state="visible")
        await page.focus(selector)

        for char in text:
            # Simulate slight delay between characters
            await page.type(selector, char, delay=random.randint(40, 120))

            # 2% chance of a "mistake" (typing a random char then backspacing)
            if random.random() < 0.02:
                await page.keyboard.press("KeyZ")  # Random char
                await asyncio.sleep(random.uniform(0.1, 0.3))
                await page.keyboard.press("Backspace")

    async def take_screenshot(self, page: Page, name: str) -> str:
        """Captures a screenshot for AI analysis or error logging."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        path = self.screenshot_dir / filename
        await page.screenshot(path=str(path))
        return str(path)

    async def upload_file(self, page: Page, selector: str, file_path: Path):
        """Safe file upload helper."""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        await page.set_input_files(selector, str(file_path))
        await asyncio.sleep(random.uniform(1.0, 2.0))  # Wait for upload processing
