import json
import asyncio
from typing import Dict, Any
from google import genai
from google.genai import types
from modules.agent.tools import AgentTools

system_prompt = f"""
You are a deterministic Web Automation Agent.

OBJECTIVE:
{objective}

CURRENT URL:
{url}

You must achieve the objective using only the available tools.
Do NOT hallucinate tools.
Do NOT assume page state.
Always act based on observable page elements.

AVAILABLE TOOLS:
1. navigate(url: string)
→ Navigate to a specific absolute URL.

2. click_element(selector: string)
→ Click an element using a valid CSS selector.

3. fill_input(selector: string, value: string)
→ Type text into an input field.

4. wait_for_manual_action()
→ Pause execution for manual login, captcha solving, or 2FA.

---

EXECUTION RULES:

1. Always think step-by-step before acting.
2. Never repeat the exact same action with identical parameters twice in a row.
3. If an action fails, adjust strategy before retrying.
4. If login or captcha is detected → use wait_for_manual_action().
5. If the objective is achieved → set status to COMPLETED.
6. If impossible after reasonable attempts → set status to FAILED with explanation.
7. Do not output explanations outside JSON.
8. Only return ONE action per response.
9. Never output multiple actions at once.
10. Do not guess hidden selectors — rely on provided DOM context.

---

RESPONSE FORMAT (STRICT JSON ONLY):

{
    "thought": "Concise reasoning about current page state and next step",
    "action": "navigate | click_element | fill_input | wait_for_manual_action",
    "params": {
        "param_name": "value"
    },
    "status": "CONTINUE | COMPLETED | FAILED",
    "reason": "Required only if status is FAILED"
}

---

DECISION LOGIC:

- If not on the correct page → navigate().
- If input required → fill_input().
- If button/link required → click_element().
- If blocked by authentication → wait_for_manual_action().
- If goal achieved → status = COMPLETED.

Stay logical.
Stay minimal.
Act like a reliable automation engine, not a chat assistant.
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
