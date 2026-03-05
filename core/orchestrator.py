import asyncio
import random
import uuid
from pathlib import Path
from typing import Dict, Any

from core.config_manager import site_config
from core.scraper import JobScraper
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status, create_sub_task
from core.custom_logging import logger
from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import UserProfile
from modules.generator.services import generate_tailored_document
from modules.generator.models import TailoredDocument


class JobOrchestrator:
    def __init__(self):
        self.ai = VanguardAI()
        self.browser = BrowserManager(headless=True)
        self.log = logger.bind(service="orchestrator")
        self.storage_path = Path("storage")
        self.scraper = JobScraper()

    async def execute_from_worker(
        self, task_id: str, user_id: str, task_type: str, bound_logger=None
    ) -> Dict[str, Any]:
        """
        Main entry point for the worker.
        Uses SiteConfig to determine target URLs and selectors.
        """
        log = bound_logger or self.log
        log.info("execution_started", task_type=task_type, task_id=task_id)

        # 1. Determine which site we are working on (defaulting to linkedin)
        # In a real scenario, this comes from task metadata
        site_name = "linkedin"
        cfg = site_config.get_site_config(site_name)

        async with self.browser.get_context(user_id=user_id) as context:
            page = await context.new_page()

            try:
                if task_type == "DISCOVERY":
                    target_url = cfg["base_url"]
                    return await self._handle_discovery(
                        page, task_id, user_id, target_url, log
                    )

                elif task_type == "AUTOMATED_APPLY":
                    return await self._handle_application(
                        page, task_id, user_id, cfg, log
                    )

            except Exception as e:
                log.error("orchestrator_critical_error", error=str(e))
                await update_task_status(task_id, TaskStatus.FAILED, error=str(e))
                return {"status": "error", "message": str(e)}

    async def _handle_discovery(self, page, task_id: str, user_id: str, url: str, log):
        """Scans for job listings and spawns sub-tasks."""
        await page.goto(url)
        await asyncio.sleep(random.uniform(2, 4))

        jobs = await self.scraper.scrape_llm(page, user_id)

        for job in jobs:
            # Chain logic: Discovery creates Apply tasks
            await create_sub_task(
                parent_task_id=task_id,
                user_id=user_id,
                task_type="AUTOMATED_APPLY",
                metadata={
                    "target_url": job.get("source_url"),
                    "job_title": job.get("job_title"),
                },
            )

        await update_task_status(task_id, TaskStatus.COMPLETED)
        return {"status": "success", "jobs_found": len(jobs)}

    async def _handle_application(
        self, page, task_id: str, user_id: str, cfg: Dict, log
    ):
        """
        Executes the autonomous application flow using ReAct logic.
        """
        task = await AgentTask.get(id=task_id)
        target_url = task.metadata.get("target_url")
        user_profile = await UserProfile.get(user_id=user_id)

        await page.goto(target_url)

        # Track history to prevent AI loops
        action_history = []
        max_steps = cfg["settings"].get("max_steps", 10)

        for step in range(max_steps):
            # Take state snapshot
            screenshot_path = await self.browser.take_screenshot(
                page, f"apply_{task_id}_step_{step}"
            )

            # AI Decision Making (ReAct)
            decision = await self.ai.analyze_screen(
                screenshot_path=screenshot_path,
                goal=f"Apply for this job: {task.metadata.get('job_title')}",
                user_id=user_id,
                history=action_history,
            )

            action = decision.get("action")
            log.info(
                "ai_step_execution",
                step=step,
                action=action,
                thought=decision.get("thought"),
            )

            if action == "COMPLETE":
                await update_task_status(task_id, TaskStatus.COMPLETED)
                return {"status": "applied"}

            if action == "AWAIT_USER":
                await update_task_status(task_id, TaskStatus.AWAITING_USER)
                return {"status": "blocked", "reason": decision.get("reason")}

            if action == "FAIL":
                raise Exception(f"AI gave up: {decision.get('reason')}")

            # Execute the action using dynamic config-based delays if needed
            await self._perform_action(page, decision, cfg)

            # Record history
            action_history.append(
                {"step": step, "action": action, "selector": decision.get("selector")}
            )

            # Human-like pause
            await asyncio.sleep(random.uniform(1.5, 3.5))

        await update_task_status(
            task_id, TaskStatus.FAILED, error="Maximum interaction steps reached"
        )
        return {"status": "failed", "reason": "step_limit_exceeded"}

    async def _perform_action(self, page, decision: Dict[str, Any], cfg: Dict):
        """Maps AI decisions to Playwright actions with config-driven timing."""
        selector = decision.get("selector")
        act_type = decision.get("action")
        value = decision.get("value")

        # Get typing delay from config
        delay_min, delay_max = cfg["settings"].get("typing_delay_range", [50, 150])

        if act_type == "CLICK":
            await page.wait_for_selector(selector, state="visible", timeout=5000)
            await page.click(selector)

        elif act_type == "TYPE":
            await page.wait_for_selector(selector, state="visible")
            await page.fill(selector, "")  # Clear existing
            await page.type(
                selector, str(value), delay=random.randint(delay_min, delay_max)
            )

        elif act_type == "SELECT":
            await page.select_option(selector, value=str(value))

        elif act_type == "UPLOAD":
            # Resume logic: In real app, fetch the actual file path from DB
            resume_path = self.storage_path / "resumes" / "default_resume.pdf"
            if resume_path.exists():
                await page.set_input_files(selector, str(resume_path))

    def _generate_notification(self, task_id: str, status: str) -> Dict[str, Any]:
        """Utility to format results for the frontend/API."""
        return {
            "task_id": task_id,
            "status": status,
            "event": "JOB_APPLICATION_UPDATE",
            "uuid": str(uuid.uuid4()),
        }
