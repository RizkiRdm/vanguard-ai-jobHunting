import asyncio
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import Optional


class BrowserEngine:
    """
    Manages the lifecycle of the Playwright browser.
    Designed to be robust and reusable across different agent tasks.
    """

    def __init__(self):
        self.pw = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

    async def start(self, headless: bool = True):
        """
        Initializes the browser instance.
        Set headless=False if you want to see what the agent is doing (debugging).
        """
        if not self.pw:
            self.pw = await async_playwright().start()

        if not self.browser:
            # Menggunakan Chromium karena paling stabil untuk scraping/automasi
            self.browser = await self.pw.chromium.launch(
                headless=headless,
                args=[
                    "--disable-blink-features=AutomationControlled"
                ],  # Menghindari deteksi bot dasar
            )

        # Membuat context dengan viewport standar laptop
        self.context = await self.browser.new_context(
            viewport={"width": 1280, "height": 720},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        )

        print("Browser Engine started successfully.")

    async def get_page(self) -> Page:
        """Creates and returns a new page in the current context."""
        if not self.context:
            await self.start()
        return await self.context.new_page()

    async def close(self):
        """Safely shuts down the browser and playwright instance."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.pw:
            await self.pw.stop()

        self.browser = None
        self.context = None
        self.pw = None
        print("Browser Engine shut down.")


# Singleton instance for easy access across the app
browser_engine = BrowserEngine()
