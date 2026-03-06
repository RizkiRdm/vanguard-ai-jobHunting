import json
import os
import re
import uuid
from typing import Dict, Any, List, Optional
from PIL import Image

from google import genai
from core.custom_logging import logger
from modules.agent.models import LLMUsageLog


class VanguardAI:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY missing")

        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.0-flash"  # Optimized for speed & cost
        self.log = logger.bind(service="vanguard-ai")

    async def analyze_screen(
        self, screenshot_path: str, goal: str, user_id: str, history: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Multimodal ReAct analysis. Decides the next browser action based on visual input.
        """
        try:
            if not os.path.exists(screenshot_path):
                raise FileNotFoundError(f"Missing screenshot: {screenshot_path}")

            image = Image.open(screenshot_path)

            # Truncate history to last 5 steps to save tokens and prevent context drift
            recent_history = history[-5:] if history else []

            system_instruction = (
                "You are an autonomous web agent. Based on the screenshot and goal, "
                "output ONLY valid JSON. Actions: CLICK, TYPE, SELECT, UPLOAD, COMPLETE, AWAIT_USER, FAIL. "
                "If you see a captcha or complex question, use AWAIT_USER."
            )

            prompt = f"""
You are a web automation agent. Your task is to achieve the following goal by interacting with the webpage shown in the screenshot.

**Goal:** {goal}

**Recent Interaction History (most recent first):**  
{json.dumps(recent_history, indent=2)}

Use this history to avoid repeating the same actions or getting stuck in loops.

---

### Instructions:
1. **Analyze the screenshot** and determine the next best action to make progress toward the goal.
2. **Output ONLY valid JSON** – no explanations, comments, or extra text.
3. The JSON must have exactly these fields:
   - `"thought"`: A brief reasoning for your chosen action.
   - `"action"`: One of the allowed actions (see below).
   - `"selector"`: A **unique CSS selector** for the element you want to interact with (if applicable). Leave empty (`""`) for actions like COMPLETE, AWAIT_USER, or FAIL.
   - `"value"`: The text to type (for TYPE), the option value to select (for SELECT), or the file path (for UPLOAD). For other actions, use `""`.
   - `"reason"`: Only required if action is `AWAIT_USER` or `FAIL`; explain why you cannot proceed. Otherwise, use `""`.

### Allowed Actions:
- **CLICK** – Click on an element (e.g., button, link). Provide the `selector`.
- **TYPE** – Type text into an input field. Provide both `selector` and `value`.
- **SELECT** – Choose an option from a dropdown. Provide `selector` and the `value` (the option text or value attribute).
- **UPLOAD** – Upload a file. Provide `selector` for the file input and `value` as the absolute path to the file.
- **COMPLETE** – Use when the goal is successfully achieved. No selector or value needed.
- **AWAIT_USER** – Use if you encounter a captcha, a complex question, or any situation requiring human intervention. Provide a `reason`.
- **FAIL** – Use if the goal cannot be completed (e.g., element missing, login required, site structure changed). Provide a `reason`.

### Examples of valid JSON outputs:
```json
{{
    "thought": "The 'Search' button is visible, clicking it will show results.",
    "action": "CLICK",
    "selector": "#search-button",
    "value": "",
    "reason": ""
}}
{{
    "thought": "Need to enter company name in the search field.",
    "action": "TYPE",
    "selector": "input[name='q']",
    "value": "Tech Companies",
    "reason": ""
}}
{{
    "thought": "A CAPTCHA appeared, cannot proceed automatically.",
    "action": "AWAIT_USER",
    "selector": "",
    "value": "",
    "reason": "CAPTCHA detected, please solve it manually."
}}
"""

            # Execute Multimodal Call
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[prompt, image],
                config={"system_instruction": system_instruction},
            )

            if not response or not response.text:
                raise ValueError("LLM_EMPTY_RESPONSE")

            # Usage Audit
            await self._log_token_usage(response, user_id)

            return self._parse_structured_response(response.text)

        except Exception as e:
            self.log.error("ai_analysis_failed", error=str(e))
            return {"action": "FAIL", "reason": str(e)}

    def _parse_structured_response(self, text: str) -> Dict[str, Any]:
        """Cleans and parses JSON from LLM markdown blocks."""
        try:
            # Extract JSON if wrapped in code blocks
            clean_json = re.sub(r"```json\s?|\s?```", "", text).strip()
            return json.loads(clean_json)
        except Exception:
            self.log.error("json_parse_error", raw_text=text)
            return {"action": "FAIL", "reason": "Invalid JSON response from AI"}

    async def _log_token_usage(self, response: Any, user_id: str) -> None:
        """Persists usage data for cost tracking and rate limiting."""
        try:
            usage = response.usage_metadata
            await LLMUsageLog.create(
                user_id=uuid.UUID(user_id),
                model_name=self.model_id,
                prompt_tokens=usage.prompt_token_count,
                completion_tokens=usage.candidates_token_count,
                total_tokens=usage.total_token_count,
            )
        except Exception as e:
            self.log.warning("usage_log_failed", error=str(e))
