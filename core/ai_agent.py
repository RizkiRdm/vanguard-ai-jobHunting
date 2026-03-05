import json
import os
import re
from typing import Dict, Any, Optional

import google.genai as genai
from core.custom_logging import logger
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

        # Use stable model version
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash"
        self.log = logger.bind(service="vanguard-ai")

    async def _log_token_usage(self, response: Any, user_id: str | None = None) -> None:
        """Securely logs token usage for auditing and billing."""
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
    async def _call_gemini_api(self, prompt: str, image: Image.Image) -> Any:
        """Wrapper for API calls with built-in retry logic."""
        return await self.client.models.generate_content(
            model=self.model_id, contents=[prompt, image]
        )

    def _clean_json_response(self, raw_text: str) -> Dict[str, Any]:
        """Robustly extracts and cleans JSON from LLM response."""
        try:
            # Remove markdown code blocks if present
            clean_text = re.sub(r"```json\s?|\s?```", "", raw_text).strip()
            # Extract only the first JSON object found
            json_match = re.search(r"(\{.*\})", clean_text, re.DOTALL)
            if not json_match:
                raise ValueError("Malformed AI Response: No JSON object found")

            return json.loads(json_match.group(1))
        except Exception as e:
            self.log.error("json_parse_error", raw_text=raw_text, error=str(e))
            return {"action": "fail", "reason": "Failed to parse AI response"}

    async def analyze_screen(
        self,
        screenshot_path: str,
        goal: str,
        user_id: str = None,
        history: Optional[list] = None,
    ) -> Dict[str, Any]:
        """
        State-aware ReAct analysis.
        'history' allows the AI to know what it did previously to avoid loops.
        """
        try:
            if not os.path.exists(screenshot_path):
                raise FileNotFoundError(f"Screenshot not found at {screenshot_path}")

            image = Image.open(screenshot_path)

            # System instructions for ReAct behavior
            system_prompt = f"""
            You are an expert Job Application Agent.
            GOAL: {goal}
            
            PREVIOUS ACTIONS: {history if history else 'None'}
            
            Instructions:
            1. Analyze the screenshot provided.
            2. Identify the current state of the application form.
            3. Choose the NEXT logical action from: [CLICK, TYPE, SELECT, UPLOAD, AWAIT_USER, COMPLETE].
            4. If the previous action failed or the screen hasn't changed, try a different approach.
            
            Return ONLY a valid JSON object:
            {{
                "thought": "Brief explanation of what you see and why this action is chosen",
                "action": "CLICK|TYPE|SELECT|UPLOAD|AWAIT_USER|COMPLETE",
                "selector": "Playwright-compatible CSS or Text selector",
                "value": "Value to type or select (if applicable)",
                "confidence": 0.0-1.0
            }}
            """

            response = await self._call_gemini_api(system_prompt, image)
            await self._log_token_usage(response, user_id)

            decision = self._clean_json_response(response.text)
            self.log.info(
                "ai_decision",
                thought=decision.get("thought"),
                action=decision.get("action"),
            )

            return decision

        except Exception as e:
            self.log.error("analysis_critical_failure", error=str(e))
            return {"action": "fail", "reason": str(e)}

    async def solve_questionnaire(
        self, screenshot_path: str, user_profile: dict
    ) -> dict:
        """Specific tool for questionnaire handling using the ReAct loop."""
        goal = f"Fill the application form using this user profile: {json.dumps(user_profile)}"
        return await self.analyze_screen(screenshot_path, goal)
