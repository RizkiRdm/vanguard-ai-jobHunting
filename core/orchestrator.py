import asyncio
import random
from pathlib import Path
from typing import Dict, Any, List

from core.scraper import JobScraper
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status, create_sub_task
from core.custom_logging import logger
from core.websocket_manager import manager  # Integrasi WebSocket
from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import UserProfile
from playwright.async_api import (
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)


class JobOrchestrator:
    def __init__(self, headless: bool = True) -> None:
        self.ai = VanguardAI()
        self.browser = BrowserManager(headless=headless)
        self.scraper = JobScraper()
        self.semaphore = asyncio.Semaphore(3)  # Max 3 concurrent browsers
        self.log = logger.bind(service="orchestrator")

    async def execute_from_worker(
        self, task_id: str, user_id: str, task_type: str
    ) -> Dict[str, Any]:

        self.log.info("execution_started", task_id=task_id, type=task_type)
        async with self.browser.get_context(user_id=user_id) as context:
            page = await context.new_page()
            try:
                if task_type == "DISCOVERY":
                    # Mengambil role impian user dari profile untuk bahan Dorking
                    profile = await UserProfile.get(user_id=user_id)
                    job_title = profile.target_role or "Software Engineer"
                    return await self._handle_discovery(
                        page, task_id, user_id, job_title
                    )

                if task_type == "AUTOMATED_APPLY":
                    return await self._handle_application(page, task_id, user_id)

                raise ValueError(f"Unsupported task type: {task_type}")

            except PlaywrightError as pw_err:
                await update_task_status(
                    task_id, TaskStatus.FAILED, error=f"Browser crash: {str(pw_err)}"
                )
                return {"status": "error", "message": str(pw_err)}

    async def _handle_discovery(
        self, page, task_id: str, user_id: str, job_title: str
    ) -> Dict[str, Any]:
        """Mencari lowongan menggunakan Google Dorking."""
        # Memberitahu UI bahwa proses pencarian dimulai
        await manager.send_personal_message(
            {"type": "INFO", "msg": f"Starting Dorking for {job_title}"}, user_id
        )

        jobs = await self.scraper.perform_dorking_search(page, job_title, user_id)

        for job in jobs:
            await create_sub_task(
                parent_task_id=task_id,
                user_id=user_id,
                task_type="AUTOMATED_APPLY",
                metadata={
                    "target_url": job.get("source_url"),
                    "job_title": job.get("job_title"),
                    "company": job.get("company_name"),
                },
            )

        await update_task_status(task_id, TaskStatus.COMPLETED)
        return {"status": "success", "spawned_tasks": len(jobs)}

    async def _handle_application(
        self, page, task_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Main ReAct loop yang di-broadcast ke WebSocket."""
        async with self.semaphore:
            task = await AgentTask.get(id=task_id)
            profile = await UserProfile.get(user_id=user_id)

            try:
                await page.goto(task.metadata["target_url"], timeout=30000)
            except PlaywrightTimeoutError:
                raise RuntimeError("Target company website took too long to load.")

            history: List[Dict] = []
            max_steps = 12
            application_goal = (
                f"Apply for {task.metadata['job_title']}. "
                f"User Profile: {profile.summary}. Expected Salary: {profile.expected_salary}."
            )

            for step in range(max_steps):
                screenshot = await self.browser.take_screenshot(
                    page, f"{task_id}_step_{step}"
                )

                decision = await self.ai.analyze_screen(
                    screenshot_path=screenshot,
                    goal=application_goal,
                    user_id=user_id,
                    history=history,
                )

                action = decision.get("action")
                thought = decision.get("thought")

                # --- WEBSOCKET STREAMING ---
                await manager.send_personal_message(
                    {
                        "type": "AGENT_STREAM",
                        "task_id": task_id,
                        "step": step,
                        "thought": thought,
                        "action": action,
                        "screenshot_url": f"/agent/tasks/{task_id}/screenshot",
                    },
                    user_id=user_id,
                )

                if action == "COMPLETE":
                    await update_task_status(task_id, TaskStatus.COMPLETED)
                    return {"status": "success"}

                if action == "AWAIT_USER":
                    await update_task_status(
                        task_id, TaskStatus.AWAITING_USER, error=decision.get("reason")
                    )
                    return {
                        "status": "waiting_for_user",
                        "question": decision.get("reason"),
                    }

                if action == "FAIL":
                    raise RuntimeError(
                        f"AI encountered a blocker: {decision.get('reason')}"
                    )

                await self._dispatch_action(page, decision)

                history.append(
                    {
                        "step": step,
                        "action": action,
                        "selector": decision.get("selector"),
                        "thought": thought,
                    }
                )
                await asyncio.sleep(random.uniform(1, 3))

            await update_task_status(
                task_id, TaskStatus.FAILED, error="Max steps exceeded"
            )
            return {"status": "failed", "reason": "max_steps_reached"}

    async def _dispatch_action(self, page, decision: Dict) -> None:
        sel = decision.get("selector")
        act = decision.get("action")
        val = decision.get("value")

        try:
            if act == "CLICK":
                await page.click(sel, timeout=5000)
            elif act == "TYPE":
                await page.fill(sel, "")
                await page.type(sel, str(val), delay=random.randint(50, 150))
            elif act == "SELECT":
                await page.select_option(sel, value=str(val))
            elif act == "UPLOAD":
                resume_path = Path("storage/resumes/active_resume.pdf")
                if resume_path.exists():
                    await page.set_input_files(sel, str(resume_path))
        except PlaywrightTimeoutError:
            self.log.warning("element_interaction_timeout", selector=sel)
