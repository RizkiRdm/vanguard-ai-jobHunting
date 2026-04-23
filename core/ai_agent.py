import json
import os
import re
import uuid
from typing import Dict, Any, List
from PIL import Image

from google import genai
from google.genai.errors import APIError
from core.custom_logging import logger
from modules.agent.models import AgentLLMUsageLog as LLMUsageLog


class VanguardAI:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing from environment variables")

        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"
        self.log = logger.bind(service="vanguard-ai")

    async def check_budget_limit(self, user_id: str) -> bool:
        """Memastikan user tidak melebihi budget harian (contoh: 10M tokens)."""
        from tortoise.functions import Sum
        from datetime import datetime, timezone

        today = datetime.now(timezone.utc).date()
        usage = (
            await LLMUsageLog.filter(user_id=user_id, created_at__gte=today)
            .annotate(total=Sum("total_tokens"))
            .first()
        )

        if usage and usage.total and usage.total > 10_000_000:
            self.log.error("budget_exceeded", user_id=user_id, total_used=usage.total)
            return False
        return True

    async def analyze_screen(
        self, screenshot_path: str, goal: str, user_id: str, history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Multimodal ReAct analysis dengan Budgeting dan Error Handling presisi."""
        # 1. Budget Check
        if not await self.check_budget_limit(user_id):
            return {
                "action": "FAIL",
                "reason": "Daily token budget exceeded. Bot stopped to save costs.",
            }

        try:
            if not os.path.exists(screenshot_path):
                raise FileNotFoundError(f"Missing screenshot: {screenshot_path}")

            image = Image.open(screenshot_path)
            recent_history = history[-5:] if history else []

            system_instruction = (
                "You are an autonomous web agent. Output ONLY valid JSON. "
                "If you encounter a form field you cannot answer, use action: 'AWAIT_USER'. "
                "Schema for AWAIT_USER reason: { 'fields': [{'id': 'key', 'label': 'Question?', 'type': 'text'}], 'reason': 'Context' }"
            )

            prompt = f"""
            Goal: {goal}
            Recent History: {json.dumps(recent_history, indent=2)}
            
            Return ONLY JSON containing: thought, action, selector, value, reason.
            Actions allowed: CLICK, TYPE, SELECT, UPLOAD, COMPLETE, AWAIT_USER, FAIL.
            """

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, image],
                config={"system_instruction": system_instruction},
            )

            if not response or not response.text:
                raise ValueError("LLM returned an empty response body.")

            await self._log_token_usage(response, user_id)
            return self._parse_structured_response(response.text)

        except FileNotFoundError as fnf_error:
            self.log.error("image_processing_failed", error=str(fnf_error))
            return {
                "action": "FAIL",
                "reason": "System failed to capture browser screen.",
            }

        except APIError as api_error:
            self.log.error("genai_api_error", error=str(api_error))
            return {
                "action": "FAIL",
                "reason": "AI Provider is currently unavailable or rate-limited.",
            }

        except ValueError as val_error:
            self.log.error("invalid_ai_response", error=str(val_error))
            return {"action": "FAIL", "reason": "AI returned an unprocessable format."}

    def _parse_structured_response(self, text: str) -> Dict[str, Any]:
        """Ekstraksi JSON yang tahan banting terhadap markdown."""
        try:
            clean_json = re.sub(r"```json\s?|\s?```", "", text).strip()
            return json.loads(clean_json)
        except json.JSONDecodeError as jde:
            self.log.error("json_parse_error", raw_text=text, error=str(jde))
            return {"action": "FAIL", "reason": "AI failed to format JSON correctly."}

    async def _log_token_usage(self, response: Any, user_id: str) -> None:
        """Pencatatan token untuk penegakan Budget Cap."""
        try:
            usage = response.usage_metadata
            await LLMUsageLog.create(
                user_id=uuid.UUID(user_id),
                model_name=self.model_id,
                prompt_tokens=usage.prompt_token_count,
                completion_tokens=usage.candidates_token_count,
                total_tokens=usage.total_token_count,
            )
        except AttributeError as attr_err:
            self.log.warning("usage_metadata_missing", error=str(attr_err))
