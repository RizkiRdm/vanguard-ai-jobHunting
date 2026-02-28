import json
<<<<<<< HEAD
import re
from typing import List, Dict, Any, Optional
from core.ai_agent import VanguardAI
from core.custom_logging import logger
from core.config_manager import site_config
=======
from typing import List, Dict, Any
from core.browser import BrowserManager
from core.ai_agent import VanguardAI
from core.custom_logging import logger
>>>>>>> 8a68e69 (refactor(core): improve scraping reliability and mock stability)
from modules.generator.models import ScrapedJob


class JobScraper:
    def __init__(self):
        self.ai = VanguardAI()
        self.log = logger.bind(service="job_scraper")

<<<<<<< HEAD
    def _sanitize_content(self, text: str) -> str:
        """
        Cleans the scraped text to prevent prompt injection and remove noise.
        """
        # Remove script and style blocks
        text = re.sub(
            r"<(script|style).*?>.*?</\1>", "", text, flags=re.DOTALL | re.IGNORECASE
        )
        # Remove HTML tags but keep content
        text = re.sub(r"<.*?>", "", text)
        # Neutralize common prompt injection keywords
        forbidden_patterns = [
            r"ignore previous instructions",
            r"system prompt",
            r"you are now an admin",
            r"output only the word",
        ]
        for pattern in forbidden_patterns:
            text = re.sub(
                pattern, "[REDACTED_INJECTION_ATTEMPT]", text, flags=re.IGNORECASE
            )

        # Normalize whitespace
        return " ".join(text.split())

    def _extract_json_from_text(self, text: str) -> Optional[dict]:
        """
        Robustly extracts the first JSON block found in the LLM response.
        Handles markdown code blocks and conversational fluff.
        """
        try:
            # Look for content between the first { and the last }
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return json.loads(text)
        except (json.JSONDecodeError, ValueError, AttributeError):
            return None

    async def scrape_llm(
        self, page, user_id: str, site_name: str = "linkedin"
    ) -> List[Dict[str, Any]]:
        """
        Advanced extraction using AI with built-in injection protection.
        """
        # 1. Capture and sanitize content
        raw_text = await page.evaluate("() => document.body.innerText")
        clean_content = self._sanitize_content(
            raw_text[:20000]
        )  # Cap at 20k chars for efficiency

        prompt = f"""
        Extract job listing details from the following text into a structured JSON format.
        
        Rules:
        - If data is missing, use null.
        - Requirements must be an array of strings.
        - Return ONLY a single JSON object.

        Text to parse:
        ---
        {clean_content}
        ---

        Output Schema:
        {{
            "job_title": "string",
            "company_name": "string",
            "location": "string",
            "employment_type": "string",
            "salary_range": "string",
            "job_description": "string",
            "requirements": ["string"],
            "source_url": "{page.url}"
        }}
        """

        try:
            # Use the existing AI client
=======
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
>>>>>>> 8a68e69 (refactor(core): improve scraping reliability and mock stability)
            response = await self.ai.client.models.generate_content(
                model=self.ai.model_id, contents=prompt
            )

<<<<<<< HEAD
            if not response or not response.text:
                raise ValueError("LLM returned an empty response")

            extracted_data = self._extract_json_from_text(response.text)

            if not extracted_data:
                self.log.error("json_extraction_failed", raw_text=response.text[:200])
                return []

            # Ensure source_url is correct
            extracted_data["source_url"] = page.url

            # Audit usage
            await self.ai._log_token_usage(response, user_id)

            # Persist to DB
            try:
                await ScrapedJob.create(user_id=user_id, **extracted_data)
                self.log.info("job_archived", title=extracted_data.get("job_title"))
            except Exception as db_err:
                self.log.warning("db_storage_failed", error=str(db_err))

            return [extracted_data]

        except Exception as e:
            self.log.error("llm_scraping_error", error=str(e))
            return []

    async def scrape_traditional(self, page, site_name: str) -> Dict[str, Any]:
        """
        Fast fallback scraping using selectors defined in config/jobsites.yaml.
        """
        self.log.info("scraping_fallback_traditional", site=site_name)
        cfg = site_config.get_site_config(site_name)
        selectors = cfg.get("selectors", {})

        async def get_text(sel):
            if not sel:
                return "Unknown"
            try:
                element = await page.query_selector(sel)
                return (await element.inner_text()).strip() if element else "Unknown"
            except:
                return "Unknown"

        return {
            "job_title": await get_text(selectors.get("job_title_selector")),
            "company_name": await get_text(selectors.get("company_selector")),
            "location": await get_text(selectors.get("location_selector")),
            "source_url": page.url,
        }
=======
            extracted_data = json.loads(response.text)

            # Audit log using existing private method (optional but recommended)
            await self.ai._log_token_usage(response, user_id)

            # Save to Database
            await ScrapedJob.create(user_id=user_id, **extracted_data)

            return extracted_data

        except Exception as e:
            self.log.error("llm_scraping_failed", error=str(e))
            return {}  # This causes KeyError if not handled in tests
>>>>>>> 8a68e69 (refactor(core): improve scraping reliability and mock stability)
