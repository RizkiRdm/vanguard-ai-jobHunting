import os
import random
from datetime import datetime
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Page


class BrowserManager:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.screenshot_dir = "storage/screenshots"
        os.makedirs(self.screenshot_dir, exist_ok=True)

    @asynccontextmanager
    async def get_context(self):
        async with async_playwright() as p:
            # Menggunakan stealth-like args agar tidak mudah terdeteksi LinkedIn
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled"],
            )
            # Menambahkan locale dan timezone agar terlihat seperti user asli
            context = await browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
                locale="en-US",
                timezone_id="Asia/Jakarta",
            )
            try:
                yield context
            finally:
                await context.close()
                await browser.close()

    async def get_page_state(self, page: Page):
        """
        Mengambil snapshot visual dan teks untuk dianalisis oleh VanguardAI.
        Ini adalah 'Input' utama untuk AI menentukan langkah selanjutnya.
        """
        screenshot_path = os.path.join(
            self.screenshot_dir, f"state_{int(datetime.now().timestamp())}.png"
        )
        await page.screenshot(path=screenshot_path)

        # Ambil teks yang terlihat saja (clean)
        content = await page.evaluate("() => document.body.innerText")
        return {"screenshot": screenshot_path, "text": content}

    async def execute_action(self, page: Page, action: dict):
        """
        Mengeksekusi perintah dari AI.
        Contoh input action: {"type": "click", "selector": "#apply-btn"}
        """
        act_type = action.get("type")
        selector = action.get("selector")

        if act_type == "click":
            await page.click(selector, delay=random.randint(200, 600))
        elif act_type == "type":
            await self.human_type(page, selector, action.get("value", ""))
        elif act_type == "wait":
            await page.wait_for_timeout(action.get("ms", 2000))

    async def human_type(self, page: Page, selector: str, text: str):
        await page.focus(selector)
        for char in text:
            await page.type(selector, char, delay=random.randint(50, 150))
