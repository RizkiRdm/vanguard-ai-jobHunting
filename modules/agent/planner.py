import json
import asyncio
from typing import Dict, Any
from google import genai
from google.genai import types
from modules.agent.tools import AgentTools


class AgentPlanner:
    """
    The reasoning engine that implements the Observe-Think-Act loop.
    Uses Gemini 2.5 Flash to decide the next best action based on page state.
    """

    def __init__(self, tools: AgentTools, api_key: str):
        self.tools = tools
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-2.5-flash-preview-09-2025"
        self.max_steps = 15  # Prevent infinite loops
        self.history = []

    async def execute_task(self, objective: str):
        """
        Starts the autonomous loop to achieve a specific objective.
        """
        print(f"Starting task: {objective}")

        for step in range(self.max_steps):
            # 1. OBSERVE: Get current state of the page
            page_content = await self.tools.scrape_page_content()
            current_url = self.tools.page.url

            # 2. THINK: Ask Gemini what to do next
            action_plan = await self._get_next_action(
                objective, page_content, current_url
            )

            # Log the thought process
            print(f"Step {step+1} Thought: {action_plan.get('thought')}")

            # Check if objective is reached
            if action_plan.get("status") == "COMPLETED":
                print("Objective achieved successfully.")
                break

            if action_plan.get("status") == "FAILED":
                raise Exception(f"Agent gave up: {action_plan.get('reason')}")

            # 3. ACT: Execute the decided tool
            await self._dispatch_action(action_plan)

            # Small delay to let the page settle
            await asyncio.sleep(2)

    async def _get_next_action(
        self, objective: str, context: str, url: str
    ) -> Dict[str, Any]:
        """
        Consults Gemini to determine the next action in JSON format.
        """
        system_prompt = f"""
        You are a Professional Web Automation Agent. Your goal: {objective}
        Current URL: {url}
        
        Available Tools:
        1. navigate(url): Go to a specific URL.
        2. click_element(selector): Click a button or link using CSS selector.
        3. fill_input(selector, value): Type text into an input field.
        4. wait_for_manual_action(): Pause for Captcha or manual login.
        
        Response Format (Strict JSON):
        {{
            "thought": "your reasoning here",
            "action": "tool_name", 
            "params": {{"param_name": "value"}},
            "status": "CONTINUE | COMPLETED | FAILED",
            "reason": "only if failed"
        }}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=f"Page Content:\n{context[:5000]}",  # Limit context to save tokens
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error consulting Gemini: {e}")
            return {"status": "FAILED", "reason": "AI Reasoning error"}

    async def _dispatch_action(self, plan: Dict[str, Any]):
        """
        Maps the AI's JSON action to the actual AgentTools functions.
        """
        action = plan.get("action")
        params = plan.get("params", {})

        if action == "navigate":
            await self.tools.navigate(params.get("url"))
        elif action == "click_element":
            await self.tools.click_element(params.get("selector"))
        elif action == "fill_input":
            await self.tools.fill_input(params.get("selector"), params.get("value"))
        elif action == "wait_for_manual_action":
            await self.tools.wait_for_manual_action()
        else:
            print(f"Unknown action requested: {action}")
