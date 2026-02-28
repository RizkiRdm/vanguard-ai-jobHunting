import json
from typing import List, Dict, Any
from core.browser import BrowserManager
from core.ai_agent import VanguardAI
from core.custom_logging import logger
from modules.generator.models import ScrapedJob


class JobScraper:
    def __init__(self):
        self.ai = VanguardAI()
        self.log = logger.bind(service="job_scraper")

    def _recursive_chunking(
        self, text: str, max_chars: int = 4000, overlap: int = 200
    ) -> List[str]:
        """
        Splits text into smaller chunks with overlap to maintain context.
        """
        chunks = []
        start = 0
        while start < len(text):
            end = start + max_chars
            chunks.append(text[start:end])
            start += max_chars - overlap
        return chunks

    async def scrape_traditional(self, page) -> Dict[str, Any]:
        """
        Version 1: Traditional Scraping using CSS Selectors.
        Fast, zero cost, but fragile to UI changes.
        """
        self.log.info("scraping_method_traditional")
        try:
            # Contoh untuk LinkedIn/Generic
            data = {
                "job_title": await page.inner_text("h1") or "",
                "company_name": await page.inner_text(".job-details-company-name")
                or "",
                "location": await page.inner_text(".job-details-location") or "",
                "source_url": page.url,
            }
            return data
        except Exception as e:
            self.log.error("traditional_scraping_failed", error=str(e))
            return {}

    async def scrape_llm(self, page, user_id: str) -> Dict[str, Any]:
        """
        AI-Driven Scraping using existing VanguardAI client.
        """
        self.log.info("scraping_method_llm", user_id=user_id)

        raw_content = await page.evaluate("() => document.body.innerText")
        chunks = self._recursive_chunking(raw_content)
        target_content = chunks[0]

        prompt = f"""
You are a structured data extraction engine.

Task:
Extract job listing information from the provided content.

STRICT RULES:
- Return ONLY valid JSON.
- Do NOT include explanations.
- Do NOT include markdown.
- Do NOT wrap in backticks.
- Do NOT add extra fields.
- If a field is not found, return null.
- requirements must always be an array (empty list if none found).
- Do not hallucinate missing information.

JSON Schema:
{{
    "job_title": string | null,
    "company_name": string | null,
    "location": string | null,
    "employment_type": string | null,
    "salary_range": string | null,
    "job_description": string | null,
    "requirements": string[],
    "source_url": "{page.url}",
    "posted_date": string | null
}}

Extraction Guidelines:
- Keep job_description concise but complete.
- Normalize whitespace.
- Remove duplicated text.
- requirements should contain only clear qualification or skill statements.
- Do not invent salary or dates.

Content to parse:

{target_content}

Return JSON only.
"""

        try:
            # Access the SDK client directly from VanguardAI to avoid adding new methods
            response = await self.ai.client.models.generate_content(
                model=self.ai.model_id, contents=prompt
            )

            extracted_data = json.loads(response.text)

            # Audit log using existing private method (optional but recommended)
            await self.ai._log_token_usage(response, user_id)

            # Save to Database
            await ScrapedJob.create(user_id=user_id, **extracted_data)

            return extracted_data

        except Exception as e:
            self.log.error("llm_scraping_failed", error=str(e))
            return {}  # This causes KeyError if not handled in tests
