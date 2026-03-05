import json
import re
from typing import List, Dict, Any, Optional
from core.ai_agent import VanguardAI
from core.custom_logging import logger
from core.config_manager import site_config
from modules.generator.models import ScrapedJob


class JobScraper:
    def __init__(self):
        self.ai = VanguardAI()
        self.log = logger.bind(service="job_scraper")

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
            response = await self.ai.client.models.generate_content(
                model=self.ai.model_id, contents=prompt
            )

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
