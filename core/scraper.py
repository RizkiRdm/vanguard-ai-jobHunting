import json
import re
from typing import List, Dict, Any, Optional
from core.ai_agent import VanguardAI
from core.custom_logging import logger
from modules.generator.models import ScrapedJob


class JobScraper:
    def __init__(self):
        self.ai = VanguardAI()
        self.log = logger.bind(service="job_scraper")

    def _sanitize_content(self, text: str) -> str:
        """Removes potential prompt injection patterns and excess noise."""
        # Remove scripts, styles, and limit repetitive characters
        sanitized = re.sub(r"<script_.*?>.*?</script>", "", text, flags=re.DOTALL)
        # Basic defense: neutralizing command-like strings
        forbidden_keywords = ["ignore previous", "system prompt", "as an admin"]
        for kw in forbidden_keywords:
            sanitized = sanitized.replace(kw, "[REDACTED]")
        return sanitized.strip()

    def _extract_json_from_text(self, text: str) -> Optional[dict]:
        """Robustly extracts JSON even if AI adds conversational text or markdown."""
        try:
            # Look for the first '{' and last '}'
            match = re.search(r"(\{.*\})", text, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            return json.loads(text)
        except (json.JSONDecodeError, ValueError):
            return None

    async def scrape_llm(self, page, user_id: str) -> List[Dict[str, Any]]:
        """
        Advanced LLM-based scraping with injection protection and robust parsing.
        """
        raw_content = await page.evaluate("() => document.body.innerText")
        target_content = self._sanitize_content(
            raw_content[:15000]
        )  # Limit context window

        prompt = f"""
        Extract job listing data from the provided text into a strict JSON format.
        
        Guidelines:
        - Use ONLY information from the text.
        - If a field is missing, use null.
        - Requirements must be an array of strings.
        
        Desired JSON Structure:
        {{
            "job_title": string,
            "company_name": string,
            "location": string,
            "employment_type": string,
            "salary_range": string,
            "job_description": string,
            "requirements": [],
            "source_url": "{page.url}",
            "posted_date": string
        }}

        Content to Parse:
        ---
        {target_content}
        ---
        Return ONLY valid JSON.
        """

        try:
            # Call AI via the centralized Gemini client
            response = await self.ai.client.models.generate_content(
                model=self.ai.model_id, contents=prompt
            )

            if not response or not response.text:
                raise ValueError("Empty response from AI model")

            extracted_data = self._extract_json_from_text(response.text)

            if not extracted_data:
                self.log.error("json_parsing_failed", raw_text=response.text[:100])
                return []

            # Token audit
            await self.ai._log_token_usage(response, user_id)

            # Integrity Check: Ensure source_url is always present
            extracted_data["source_url"] = page.url

            # Database Persistence
            try:
                await ScrapedJob.create(user_id=user_id, **extracted_data)
                self.log.info(
                    "job_saved_to_db", job_title=extracted_data.get("job_title")
                )
            except Exception as db_err:
                self.log.warning("db_save_failed_but_returning_data", error=str(db_err))

            return [extracted_data]

        except Exception as e:
            self.log.error("llm_scraping_critical_failure", error=str(e))
            return []

    async def scrape_traditional(self, page) -> Dict[str, Any]:
        """Fallback method using standard CSS selectors."""
        self.log.info("scraping_method_traditional")
        # Implementation remains similar but with more robust null checking
        return {
            "job_title": (await page.inner_text("h1") or "Unknown").strip(),
            "company_name": (
                await page.inner_text(".job-details-company-name") or "Unknown"
            ).strip(),
            "source_url": page.url,
        }
