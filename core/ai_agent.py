import json
import os
import re
from pathlib import Path

import google.genai as genai
from core.logging import logger
from dotenv import load_dotenv
from modules.agent.models import LLMUsageLog
from PIL import Image
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

load_dotenv()


class VanguardAI:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash"
        self.log = logger.bind(service="vanguard-ai")

    async def _log_token_usage(self, response: any, user_id: str | None = None) -> None:
        # Save token usage to database
        try:
            usage = response.usage_metadata
            await LLMUsageLog.create(
                user_id=user_id,
                prompt_tokens=usage.prompt_token_count,
                completion_tokens=usage.candidates_token_count,
                total_tokens=usage.total_token_count,
                model_name=self.model_id,
            )
            self.log.info("token_audit_saved", total_tokens=usage.total_token_count)
        except Exception as e:
            self.log.error("token_audit_failed", error=str(e))

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
    )
    async def _call_gemini_api(self, prompt: str, image: Image.Image) -> any:
        # Execute remote GenAI request
        return await self.client.models.generate_content(
            model=self.model_id, contents=[prompt, image]
        )

    async def analyze_screen(
        self, screenshot_path: str, goal: str, user_id: str | None = None
    ) -> dict:
        # Main analysis flow
        self.log.info("ai_analysis_started", user_id=user_id)

        try:
            # Load image and prompt
            image = Image.open(screenshot_path)
            prompt_template = Path("prompts/agent_prompt.md").read_text()
            prompt = prompt_template.replace("{{goal}}", goal)

            # API Execution
            response = await self._call_gemini_api(prompt, image)

            # Deterministic logging (Wait for DB)
            await self._log_token_usage(response, user_id)

            # Parsing
            return self._parse_response(response.text)

        except Exception as e:
            self.log.error("analysis_failed", error=str(e))
            return {"action": "fail", "reasoning": str(e)}

    def _parse_response(self, raw_text: str) -> dict:
        # Extract JSON from response text
        json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
        if not json_match:
            raise ValueError("No valid JSON found in model response")

        decision = json.loads(json_match.group(0))
        self.log.info("ai_decision_made", action=decision.get("action"))
        return decision
