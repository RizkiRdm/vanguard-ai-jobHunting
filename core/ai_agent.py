import json
import os
import re
from typing import Dict, Any, Optional
import uuid

from google import genai
from core.custom_logging import logger
from dotenv import load_dotenv
from modules.agent.models import LLMUsageLog
from PIL import Image

load_dotenv()


class VanguardAI:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # Initialize the new Google Gen AI Client
        self.client = genai.Client(api_key=api_key)

        self.model_id = "gemini-2.5-flash"
        self.log = logger.bind(service="vanguard-ai")

    async def _log_token_usage(self, response: Any, user_id: str | None = None) -> None:
        """Logs token usage to database for auditing."""
        try:
            try:
                valid_user_id = uuid.UUID(str(user_id)) if user_id else None
            except ValueError:
                self.log.warning("invalid_uuid_skipping_audit", provided_id=user_id)
                return
            # According to SDK docs, usage is in usage_metadata
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

    def _clean_json_response(self, raw_text: str) -> Dict[str, Any]:
        """Robustly extracts JSON from LLM response text."""
        try:
            # Remove markdown formatting if present
            clean_text = re.sub(r"```json\s?|\s?```", "", raw_text).strip()
            json_match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON block found in response")
            return json.loads(json_match.group(1))
        except Exception as e:
            self.log.error("json_parse_error", raw_text=raw_text, error=str(e))
            return {"action": "fail", "reason": "Parsing error"}

    async def analyze_screen(
        self,
        screenshot_path: str,
        goal: str,
        user_id: str = None,
        history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        ReAct implementation using the latest Google Gen AI SDK.
        """
        try:
            if not os.path.exists(screenshot_path):
                raise FileNotFoundError(f"Screenshot not found: {screenshot_path}")

            # Load image for multimodal input
            image = Image.open(screenshot_path)

            # Structured prompt for ReAct
            prompt = f"""
            Task: {goal}
            Current History: {history if history else 'First step'}
            
            Analyze the screenshot and return ONLY a JSON object:
            {{
                "thought": "Reasoning about current state",
                "action": "CLICK|TYPE|SELECT|UPLOAD|COMPLETE|AWAIT_USER",
                "selector": "CSS selector if applicable",
                "value": "Value to input if applicable",
                "confidence": 0.95
            }}
            """

            # CALL API using the new SDK syntax (from README.md)
            # We use list [prompt, image] for multimodal
            response = self.client.models.generate_content(
                model=self.model_id, contents=[prompt, image]
            )

            if not response or not response.text:
                raise ValueError("API returned empty response")

            # Usage Logging
            await self._log_token_usage(response, user_id)

            # Parsing
            return self._clean_json_response(response.text)

        except Exception as e:
            self.log.error("analysis_critical_failure", error=str(e))
            return {"action": "fail", "reason": str(e)}
