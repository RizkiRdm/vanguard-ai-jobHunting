import os
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Browser, BrowserContext, Page


class BrowserManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.screenshot_dir = "storage/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    @asynccontextmanager
    async def get_context(self):
        """
        Context Manager to ensure browser resources are closed safely.
        Prevents zombie processes/memory leaks.
        """
        async with async_playwright() as p:
            # Launch with optimization flags for the Docker/Linux environment
            browser = await p.chromium.launch(
                headless=self.headless, args=["--disable-dev-shm-usage", "--no-sandbox"]
            )
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Vanguard-Agent/1.0 (AI Job Hunting Copilot)",
            )
            try:
                yield context
            finally:
                # Ensuring resources are cleaned up no matter what happens
                await context.close()
                await browser.close()

    async def take_failure_screenshot(self, page: Page, task_id: str):
        """
        Capturing visual evidence if the task fails.
        Stored in storage/screenshots/.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"FAIL_{task_id}_{timestamp}.png"
        path = os.path.join(self.screenshot_dir, filename)
        await page.screenshot(path=path, full_page=True)
        return path

    async def simple_navigate(self, url: str, task_id: str = "manual_test"):
        """
        Basic navigation helper function with failure protection.
        """
        async with self.get_context() as context:
            page = await context.new_page()
            try:
                # Timeout 30 seconds
                await page.goto(url, wait_until="networkidle", timeout=30000)
                return await page.title()
            except Exception as e:
                # DoD: Screenshot on failure
                path = await self.take_failure_screenshot(page, task_id)
                print(f"[BROWSER ERROR] Task {task_id} failed. Evidence: {path}")
                raise e
