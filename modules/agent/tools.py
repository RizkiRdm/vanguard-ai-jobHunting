import asyncio
import os
from datetime import datetime
from playwright.async_api import Page, ElementHandle
from typing import Optional, List, Dict


class AgentTools:
    """
    A collection of navigation and extraction functions for the Agent.
    Designed to be called by the Planner (Reasoning Loop).
    """

    def __init__(self, page: Page, screenshot_dir: str = "static/screenshots"):
        self.page = page
        self.screenshot_dir = screenshot_dir
        if not os.path.exists(self.screenshot_dir):
            os.makedirs(self.screenshot_dir)

    async def take_screenshot(self, name: str) -> str:
        """Captures a screenshot for logging and debugging purposes."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{self.screenshot_dir}/{name}_{timestamp}.png"
        await self.page.screenshot(path=path)
        return path

    async def navigate(self, url: str):
        """Navigates to the target URL with timeout protection."""
        try:
            await self.page.goto(url, wait_until="networkidle", timeout=30000)
        except Exception as e:
            await self.take_screenshot("nav_error")
            raise Exception(f"Failed to navigate to {url}: {str(e)}")

    async def click_element(self, selector: str, wait_before: int = 500):
        """Clicks an element based on CSS/Text selector."""
        await asyncio.sleep(wait_before / 1000)
        try:
            # Ensure the element is visible and ready to be clicked
            await self.page.wait_for_selector(selector, state="visible", timeout=10000)
            await self.page.click(selector)
        except Exception as e:
            await self.take_screenshot("click_error")
            raise Exception(f"Failed to click element {selector}: {str(e)}")

    async def fill_input(self, selector: str, value: str):
        """Fills an input form with human-like typing simulation."""
        try:
            await self.page.wait_for_selector(selector, state="visible")
            await self.page.fill(selector, "")  # Clear existing value
            await self.page.type(
                selector, value, delay=100
            )  # Add delay to mimic human typing
        except Exception as e:
            await self.take_screenshot("fill_error")
            raise Exception(f"Failed to fill input {selector}: {str(e)}")

    async def scrape_page_content(self) -> str:
        """Extracts clean text from the page for AI analysis."""
        # Extract body text while removing scripts, styles, navigation, and footers
        content = await self.page.evaluate(
            """
            () => {
                const scripts = document.querySelectorAll('script, style, nav, footer');
                scripts.forEach(s => s.remove());
                return document.body.innerText;
            }
        """
        )
        return content.strip()

    async def find_job_listings(self, card_selector: str) -> List[Dict]:
        """Specific tool to extract a list of job postings."""
        listings = []
        try:
            elements = await self.page.query_selector_all(card_selector)
            for el in elements:
                text = await el.inner_text()
                listings.append(
                    {
                        "raw_text": text,
                        "element": el,  # Store reference for future interactions
                    }
                )
        except Exception:
            pass
        return listings

    async def wait_for_manual_action(self, timeout: int = 60000):
        """
        Pauses execution to allow for manual user intervention (e.g., Captcha/Login).
        """
        print("Waiting for manual user action (Captcha/Login)...")
        try:
            await self.page.wait_for_timeout(timeout)
        except:
            pass
