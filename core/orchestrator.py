import os
import uuid
import json
import random
from pathlib import Path
from typing import Dict, Any

from core.scraper import JobScraper
from core.security import MalwareScanner
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status
from core.custom_logging import logger
from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import User, UserProfile


class JobOrchestrator:
    def __init__(self):
        self.scanner = MalwareScanner()
        self.ai = VanguardAI()
        self.browser = BrowserManager(headless=True)
        self.log = logger.bind(service="orchestrator")
        self.storage_path = Path("storage")
        self.scraper = JobScraper()

    async def execute_from_worker(
        self, task_id: str, user_id: str, task_type: str, bound_logger=None
    ):
        """
        Refactored worker entry point supporting Autonomous Application.
        """
        log = bound_logger or self.log
        log.info("worker_execution_started", task_type=task_type, task_id=task_id)

        async with self.browser.get_context() as context:
            page = await context.new_page()

            # Case 1: Automated Job Application (The New Full Workflow)
            if task_type == "AUTOMATED_APPLY":
                task = await AgentTask.get(id=task_id)
                target_url = task.metadata.get("target_url")
                return await self.run_autonomous_apply(
                    page, user_id, task_id, target_url, log
                )

            # Case 2: Discovery / Scraping (Existing logic)
            elif task_type == "DISCOVERY":
                await page.goto(
                    "https://www.linkedin.com/jobs/...", wait_until="networkidle"
                )
                return await self.scraper.scrape_llm(page, user_id)

            return {"status": "error", "message": f"Unknown task type: {task_type}"}

    async def run_autonomous_apply(
        self, page, user_id: str, task_id: str, target_url: str, log
    ):
        """
        The core loop where the AI 'sees' the screen and 'acts' until submission.
        """
        log.info("starting_autonomous_apply", url=target_url)
        await page.goto(target_url, wait_until="networkidle")

        # Get user data to answer questions (Salary, Exp, etc.)
        user_profile = await UserProfile.get(user_id=user_id)

        max_steps = 12
        current_step = 0

        while current_step < max_steps:
            current_step += 1

            # 1. VISION: Capture current UI state
            screenshot_path = await self.browser.take_failure_screenshot(
                page, f"step_{current_step}_{task_id}"
            )

            # 2. REASONING: Ask AI for next move based on screen + user profile
            decision = await self.ai.analyze_screen(
                screenshot_path=screenshot_path,
                goal=f"Apply to this job. Profile context: {user_profile.summary}. Expected Salary: {user_profile.expected_salary or 'Market Standard'}",
                user_id=user_id,
            )

            log.info(
                "ai_decision_received", step=current_step, action=decision.get("action")
            )

            # 3. EVALUATION: Handle completion, failure, or human intervention
            if decision.get("action") == "COMPLETE":
                await update_task_status(task_id, TaskStatus.COMPLETED)
                return self._generate_final_notification(task_id, "SUCCESS")

            if decision.get("action") == "AWAIT_USER":
                await AgentTask.filter(id=task_id).update(
                    status=TaskStatus.AWAITING_USER,
                    subjective_question=decision.get("question"),
                )
                return {
                    "status": "waiting_for_user",
                    "question": decision.get("question"),
                }

            if decision.get("action") == "FAILURE":
                await update_task_status(task_id, TaskStatus.FAILED)
                return {"status": "failed", "reason": decision.get("reason")}

            # 4. ACTION: Execute physical browser movement
            try:
                await self._perform_action(page, decision)
                # Anti-detection delay
                await page.wait_for_timeout(random.randint(1000, 2500))
            except Exception as e:
                log.error("execution_error", error=str(e))
                break

        await update_task_status(task_id, TaskStatus.FAILED)
        return {"status": "failed", "reason": "Max steps exceeded"}

    async def _perform_action(self, page, decision: Dict[str, Any]):
        """Executes the low-level Playwright actions commanded by AI."""
        act_type = decision.get("action")  # e.g., 'CLICK', 'TYPE'
        selector = decision.get("selector")
        value = decision.get("value")

        if act_type == "CLICK":
            await page.click(selector)
        elif act_type == "TYPE":
            await page.fill(selector, "")  # Clear first
            await page.type(selector, str(value), delay=random.randint(50, 150))
        elif act_type == "SELECT":
            await page.select_option(selector, value=str(value))

    def _generate_final_notification(self, task_id: str, status: str) -> Dict[str, Any]:
        """Returns the structured JSON notification for the end-user."""
        return {
            "notification_type": "JOB_APPLICATION_UPDATE",
            "task_id": task_id,
            "timestamp": str(uuid.uuid4()),  # Mock timestamp
            "data": {
                "status": status,
                "platform": "LinkedIn",
                "message": "All forms successfully filled. Application is now in 'Pending Confirmation' status.",
                "action_required": False,
            },
        }
