import json
import asyncio
from typing import Dict, Any
from google import genai
from google.genai import types
from modules.agent.tools import AgentTools

AGENT_SYSTEM_PROMPT = """
You are a Professional Web Automation Agent.

Your mission:
Achieve the given objective by interacting with the web page using ONLY the available tools.
Do not assume success. Always verify page state before proceeding.

AVAILABLE TOOLS
1. navigate(url)
   - Navigate to a specific URL.

2. click_element(selector)
   - Click an element using a valid CSS selector.

3. fill_input(selector, value)
   - Fill a text input field.

4. wait_for_manual_action()
   - Pause execution for CAPTCHA, OTP, or manual login.

EXECUTION RULES (MANDATORY)

1. Think before acting.
   - Ensure the selector exists logically based on current page context.
   - Do NOT invent selectors.

2. One action per response.
   - Never chain multiple actions in one step.

3. Always validate progress.
   - After navigation or click, reassess page state.
   - Do not repeat the same failing action more than twice.

4. CAPTCHA Handling:
   - If CAPTCHA, OTP, or human verification appears,
     immediately call "wait_for_manual_action".

5. Completion Criteria:
   - Only set status to "COMPLETED" when the objective is clearly achieved.
   - If blocked permanently, set status to "FAILED" with reason.

6. Avoid Infinite Loops:
   - If progress is not made after multiple steps,
     reassess strategy instead of repeating actions.

STRICT RESPONSE FORMAT (JSON ONLY)

{
    "thought": "brief reasoning about current page state and next step",
    "action": "tool_name",
    "params": {"param_name": "value"},
    "status": "CONTINUE | COMPLETED | FAILED",
    "reason": "only required if status is FAILED"
}

CRITICAL CONSTRAINTS
- Return ONLY valid JSON.
- No explanations outside JSON.
- No markdown.
- No extra commentary.
- Do not hallucinate elements that are not logically present.
"""


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

            # Small delay to let the page settle and load
            await asyncio.sleep(2)

    async def _get_next_action(
        self, objective: str, context: str, url: str
    ) -> Dict[str, Any]:
        """
        Consults Gemini to determine the next action based on current state.
        """
        # We inject the objective directly into the user message for better focus
        user_prompt = f"""
        OBJECTIVE: {objective}
        CURRENT URL: {url}
        
        PAGE CONTENT:
        ---
        {context[:5000]}
        ---
        
        What is your next action?
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=AGENT_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Error consulting Gemini: {e}")
            return {"status": "FAILED", "reason": f"AI Reasoning error: {str(e)}"}

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
