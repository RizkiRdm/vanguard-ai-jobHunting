import os
import json
import io
import asyncio
import re
from typing import Dict, Any
from PIL import Image
from google import genai  # SDK Terbaru

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)


class VanguardAI:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        # SDK Terbaru menggunakan Client object
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-1.5-flash"

    def _prepare_image(self, image_path: str) -> Dict[str, Any]:
        """Processes and converts image to WebP format synchronously."""
        with Image.open(image_path) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            buffer = io.BytesIO()
            img.save(buffer, format="WEBP", quality=80)

            # Format return untuk SDK google-genai terbaru sedikit berbeda
            return {"mime_type": "image/webp", "data": buffer.getvalue()}

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _call_gemini_api(self, prompt: str, image_part: Dict[str, Any]):
        """Internal method using the new SDK syntax."""
        # Pada SDK baru, methodnya adalah client.models.generate_content
        return await self.client.models.generate_content(
            model=self.model_id, contents=[prompt, image_part]
        )

    async def analyze_screen(self, screenshot_path: str, goal: str) -> Dict[str, Any]:
        if not os.path.exists(screenshot_path):
            raise FileNotFoundError(f"Screenshot not found at: {screenshot_path}")

        loop = asyncio.get_event_loop()
        try:
            image_part = await loop.run_in_executor(
                None, self._prepare_image, screenshot_path
            )

            prompt = f"""
CONTEXT:
You are Vanguard AI Agent operating a browser to help a user apply for a job.

OBJECTIVE:
{goal}

INSTRUCTIONS:
You are given a browser screenshot.
Analyze the visible UI carefully and determine EXACTLY ONE next technical action.

Rules:
- Choose only ONE action.
- Prefer the most deterministic and forward-progress action.
- Do NOT guess hidden elements that are not visible.
- If loading is in progress, use "wait".
- If the objective is clearly achieved, use "complete".
- If blocked (captcha, login required, unknown state), use "fail".

Allowed Actions:
- "click" → click a visible button, link, or interactive element
- "type" → type into a visible input field
- "wait" → wait for page loading or async state
- "complete" → goal has been achieved
- "fail" → cannot proceed safely

Selector Rules:
- Use precise CSS selector if identifiable.
- If CSS selector is unclear, use visible button/text label.
- Never invent selectors that are not visible.
- For "type", selector must target an input or textarea.

Output MUST be strict JSON only.
No markdown.
No extra text.
No explanation outside JSON.

Required JSON format:
{{
    "action": "click" | "type" | "wait" | "complete" | "fail",
    "selector": "exact_css_selector_or_visible_text",
    "value": "text_to_input_if_action_is_type_else_empty_string",
    "reasoning": "brief justification based only on visible UI"
}}
"""

            # Call API
            response = await self._call_gemini_api(prompt, image_part)
            raw_text = response.text

            # Robust JSON Extraction
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                # Menggunakan json.loads pada hasil extract regex
                return json.loads(json_match.group(0))
            else:
                # PESAN ERROR DISESUAIKAN UNTUK TEST
                raise ValueError(f"No JSON object found in response: {raw_text}")

        except Exception as e:
            return {
                "action": "fail",
                "reasoning": f"Critical error: {str(e)}",
            }
