import asyncio
import random
from pathlib import Path
from typing import Dict, Any, List

from core.config_manager import site_config
from core.scraper import JobScraper
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status, create_sub_task
from core.custom_logging import logger
from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import UserProfile
from modules.generator.services import generate_tailored_document


class JobOrchestrator:
    def __init__(self, headless: bool = True):
        self.ai = VanguardAI()
        self.browser = BrowserManager(headless=headless)
        self.scraper = JobScraper()
        self.log = logger.bind(service="orchestrator")
        self.semaphore = asyncio.Semaphore(3)
        self.log = logger.bind(service="orchestrator")

    async def execute_from_worker(
        self, task_id: str, user_id: str, task_type: str
    ) -> Dict[str, Any]:
        """Entry point for task execution from the worker pool."""
        self.log.info("execution_started", task_id=task_id, type=task_type)

        # Site config defaults to linkedin if not specified in metadata
        cfg = site_config.get_site_config("linkedin")

        async with self.browser.get_context(user_id=user_id) as context:
            page = await context.new_page()
            try:
                if task_type == "DISCOVERY":
                    return await self._handle_discovery(page, task_id, user_id, cfg)

                if task_type == "AUTOMATED_APPLY":
                    return await self._handle_application(page, task_id, user_id, cfg)

                raise ValueError(f"Unsupported task type: {task_type}")

            except Exception as e:
                self.log.error(
                    "execution_critical_failure", task_id=task_id, error=str(e)
                )
                await update_task_status(task_id, TaskStatus.FAILED, error=str(e))
                return {"status": "error", "message": str(e)}

    async def _handle_discovery(
        self, page, task_id: str, user_id: str, cfg: Dict
    ) -> Dict[str, Any]:
        """Scans job boards and spawns sub-tasks for each listing."""
        await page.goto(cfg["base_url"])
        await asyncio.sleep(random.uniform(2, 5))

        jobs = await self.scraper.scrape_llm(page, user_id)

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
        self, page, task_id: str, user_id: str, cfg: Dict
    ) -> Dict[str, Any]:
        """Main ReAct loop for autonomous job application."""
        async with self.semaphore:  # Implementation of concurrency control
            task = await AgentTask.get(id=task_id)
            profile = await UserProfile.get(user_id=user_id)  # Now utilized below

            await page.goto(task.metadata["target_url"])

            history: List[Dict] = []
            max_steps = cfg["settings"].get("max_steps", 12)

            # Construct a rich goal using the user's profile data
            application_goal = (
                f"Apply for {task.metadata['job_title']} at {task.metadata.get('company')}. "
                f"User Profile: {profile.summary}. "
                f"Expected Salary: {profile.expected_salary}."
            )

            for step in range(max_steps):
                screenshot = await self.browser.take_screenshot(
                    page, f"{task_id}_step_{step}"
                )

                # AI now knows WHO it is representing
                decision = await self.ai.analyze_screen(
                    screenshot_path=screenshot,
                    goal=application_goal,
                    user_id=user_id,
                    history=history,
                )

            action = decision.get("action")
            self.log.info(
                "ai_decision", step=step, action=action, thought=decision.get("thought")
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
                raise RuntimeError(f"AI gave up: {decision.get('reason')}")

            await self._dispatch_action(page, decision, cfg)

            history.append(
                {
                    "step": step,
                    "action": action,
                    "selector": decision.get("selector"),
                    "thought": decision.get("thought"),
                }
            )

            await asyncio.sleep(random.uniform(1, 3))

        await update_task_status(task_id, TaskStatus.FAILED, error="Max steps exceeded")
        return {"status": "failed", "reason": "max_steps_reached"}

    async def _dispatch_action(self, page, decision: Dict, cfg: Dict):
        """Map AI actions to Playwright commands with config-driven timing."""
        sel = decision.get("selector")
        act = decision.get("action")
        val = decision.get("value")

        delays = cfg["settings"].get("typing_delay_range", [50, 150])

        if act == "CLICK":
            await page.click(sel, timeout=5000)

        elif act == "TYPE":
            await page.fill(sel, "")
            await page.type(sel, str(val), delay=random.randint(*delays))

        elif act == "SELECT":
            await page.select_option(sel, value=str(val))

        elif act == "UPLOAD":
            # Resume resolution logic should go here (fetch from storage/db)
            resume_path = Path("storage/resumes/active_resume.pdf")
            if resume_path.exists():
                await page.set_input_files(sel, str(resume_path))
