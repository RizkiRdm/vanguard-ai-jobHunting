import json
import re
from typing import List, Dict, Any, Optional
from core.ai_agent import VanguardAI
from core.custom_logging import logger
from modules.generator.models import ScrapedJob
from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError


class JobScraper:
    def __init__(self) -> None:
        self.ai = VanguardAI()
        self.log = logger.bind(service="job_scraper")

    def _extract_json_from_text(self, text: str) -> Optional[dict]:
        try:
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            return json.loads(match.group(1)) if match else json.loads(text)
        except json.JSONDecodeError:
            return None

    async def perform_dorking_search(
        self, page: Page, job_title: str, user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Mencari lowongan langsung di situs perusahaan menggunakan Google Dorking.
        Menghindari blokir spesifik job board.
        """
        # Query: Mencari halaman karir yang spesifik, membuang job aggregators
        query = f'"{job_title}" intitle:"careers" OR intitle:"jobs" -inurl:linkedin -inurl:jobstreet -inurl:indeed'
        search_url = f"https://www.google.com/search?q={query}"

        try:
            self.log.info("dorking_started", query=query)
            await page.goto(search_url, wait_until="domcontentloaded", timeout=15000)

            # Ekstraksi organik link dari Google Search Result
            links_locators = await page.locator("div.yuRUbf a").all()
            scraped_jobs = []

            for link in links_locators[:5]:  # Batasi 5 link pertama untuk efisiensi
                url = await link.get_attribute("href")
                if url and "google" not in url:
                    job_data = {
                        "job_title": job_title,
                        "company_name": "Extracted via Dorking",
                        "source_url": url,
                        "location": "Remote/Unspecified",
                    }
                    scraped_jobs.append(job_data)

                    # Persist ke database agar bisa di-apply oleh orchestrator
                    await ScrapedJob.create(user_id=user_id, **job_data)

            self.log.info("dorking_completed", results_found=len(scraped_jobs))
            return scraped_jobs

        except PlaywrightTimeoutError:
            self.log.error("dorking_timeout", url=search_url)
            return []
        except Exception as generic_err:
            self.log.error("dorking_failed", error=str(generic_err))
            return []
