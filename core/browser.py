import random
import asyncio
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any

from playwright.async_api import async_playwright, Page, BrowserContext, Browser
from core.custom_logging import logger


class BrowserManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.log = logger.bind(service="browser_manager")
        self.session_dir = Path("storage/sessions")
        self.screenshot_dir = Path("storage/screenshots")

        # Ensure critical directories exist
        self.session_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    async def _inject_stealth(self, page: Page):
        """
        Injects advanced evasion scripts to hide Playwright's automation signature.
        """
        await page.add_init_script(
            """
            // Hide webdriver property
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            
            // Mock Chrome runtime
            window.chrome = { runtime: {} };

            // Mock languages and plugins
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

            // Fix for hardware concurrency to look like a standard consumer laptop
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
        """
        )

    async def _get_session_path(self, user_id: str) -> Path:
        """Helper to get standardized session file path."""
        return self.session_dir / f"auth_{user_id}.json"

    @asynccontextmanager
    async def get_context(self, user_id: Optional[str] = None):
        """
        Context manager for browser sessions.
        Handles persistent state (cookies/storage) automatically.
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )

            # Setup context arguments
            context_args = {
                "viewport": {"width": 1280, "height": 800},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "locale": "en-US",
                "timezone_id": "UTC",
            }

            # Load existing session if available
            if user_id:
                session_path = await self._get_session_path(user_id)
                if session_path.exists():
                    context_args["storage_state"] = str(session_path)
                    self.log.info("session_loaded", user_id=user_id)

            context = await browser.new_context(**context_args)

            # Create a default page and apply stealth
            # Note: Init scripts must be applied to the context to affect all pages
            await self._inject_stealth(context)

            try:
                yield context

                # Auto-save session state on successful close if user_id is provided
                if user_id:
                    await context.storage_state(
                        path=str(await self._get_session_path(user_id))
                    )
                    self.log.info("session_saved", user_id=user_id)

            except Exception as e:
                self.log.error("browser_context_error", error=str(e))
                raise
            finally:
                await context.close()
                await browser.close()

    async def human_type(
        self, page: Page, selector: str, text: str, delay_range: tuple = (60, 180)
    ):
        """
        Types text into an element with variable delays and simulated human rhythm.
        """
        await page.wait_for_selector(selector, state="visible", timeout=10000)
        await page.focus(selector)

        for char in text:
            await page.type(selector, char, delay=random.randint(*delay_range))

            # 1% chance of a "thought pause" between words or characters
            if random.random() < 0.01:
                await asyncio.sleep(random.uniform(0.5, 1.2))

    async def take_screenshot(self, page: Page, name: str) -> str:
        """
        Captures a screenshot for AI vision analysis.
        Returns the absolute path to the file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.screenshot_dir / f"{name}_{timestamp}.png"
        await page.screenshot(path=str(file_path), full_page=False)
        return str(file_path.absolute())

    async def safe_click(self, page: Page, selector: str):
        """
        Click with pre-wait and slight randomization of the click coordinates.
        """
        await page.wait_for_selector(selector, state="visible")
        box = await page.locator(selector).bounding_box()
        if box:
            # Click near the center but slightly offset
            x = box["x"] + box["width"] / 2 + random.uniform(-5, 5)
            y = box["y"] + box["height"] / 2 + random.uniform(-5, 5)
            await page.mouse.click(x, y)
        else:
            await page.click(selector)
