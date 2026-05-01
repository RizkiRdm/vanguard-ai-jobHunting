import asyncio
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

from core.config_manager import site_config
from core.scraper import JobScraper
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status, create_sub_task
from core.custom_logging import logger
from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import UserProfile
from modules.generator.services import generate_tailored_document


from core.database import AsyncSessionLocal
from sqlalchemy import select

class JobOrchestrator:
    def __init__(self, headless: bool = True):
        self.ai = VanguardAI()
        self.browser = BrowserManager() # BrowserManager handles headless internally or we update it
        self.scraper = JobScraper()
        self.log = logger.bind(service="orchestrator")
        self.semaphore = asyncio.Semaphore(3)

    async def execute_from_worker(
        self, task_id: str, user_id: str, task_type: str
    ) -> Dict[str, Any]:
        """Entry point for task execution from the worker pool."""
        self.log.info("execution_started", task_id=task_id, type=task_type)

        # Site config defaults to linkedin if not specified in metadata
        cfg = site_config.get_site_config("linkedin")

        await self.browser.connect()
        try:
            # Logic refactor: MCP handles session, orchestrator just drives
            await self.browser.open_url(cfg["base_url"])
            
            if task_type == "DISCOVERY":
                return await self._handle_discovery(task_id, user_id, cfg)

            if task_type == "AUTOMATED_APPLY":
                return await self._handle_application(task_id, user_id, cfg)

            raise ValueError(f"Unsupported task type: {task_type}")
        finally:
            await self.browser.disconnect()

    async def _handle_discovery(
        self, task_id: str, user_id: str, cfg: Dict
    ) -> Dict[str, Any]:
        """Scans job boards and spawns sub-tasks for each listing."""
        # Already opened base_url in execute_from_worker
        await asyncio.sleep(random.uniform(2, 5))

        jobs = await self.scraper.scrape_llm(self.browser, user_id)

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
        self, task_id: str, user_id: str, cfg: Dict
    ) -> Dict[str, Any]:
        """Main ReAct loop for autonomous job application."""
        async with self.semaphore:
            async with AsyncSessionLocal() as db:
                task_res = await db.execute(select(AgentTask).filter_by(id=task_id))
                task = task_res.scalar_one_or_none()
                
                profile_res = await db.execute(select(UserProfile).filter_by(user_id=user_id))
                profile = profile_res.scalar_one_or_none()

                if not task or not profile:
                    raise ValueError("Task or Profile not found")

                await self.browser.open_url(task.meta_data["target_url"])

                history: List[Dict] = []
                max_steps = cfg["settings"].get("max_steps", 12)

                application_goal = (
                    f"Apply for {task.meta_data['job_title']} at {task.meta_data.get('company')}. "
                    f"User Profile: {profile.summary}. "
                    f"Expected Salary: {profile.expected_salary}."
                )

                for step in range(max_steps):
                    screenshot = await self.browser.take_screenshot(
                        f"{task_id}_step_{step}"
                    )

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

                    # Pass the profile object to dispatch to handle dynamic uploads
                    await self._dispatch_action(decision, cfg, profile)

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

    async def _dispatch_action(self, decision: Dict, cfg: Dict, profile: UserProfile):
        """Map AI actions to Playwright commands via BrowserManager."""
        sel = decision.get("selector")
        act = decision.get("action")
        val = decision.get("value")

        if act == "CLICK":
            await self.browser.perform_action("playwright_click", {"selector": sel})

        elif act == "TYPE":
            await self.browser.perform_action("playwright_fill", {"selector": sel, "value": str(val)})

        elif act == "SELECT":
            await self.browser.perform_action("playwright_select_option", {"selector": sel, "value": str(val)})

        elif act == "UPLOAD":
            # Resolve dynamic resume path from user profile
            resume_path_str = profile.resume_url if profile.resume_url else "storage/resumes/default_resume.pdf"
            resume_path = Path(resume_path_str)
            
            if resume_path.exists():
                await self.browser.perform_action("playwright_set_input_files", {"selector": sel, "files": [str(resume_path)]})
                self.log.info("resume_uploaded", path=str(resume_path))
            else:
                self.log.error("resume_file_missing", path=str(resume_path))
                raise FileNotFoundError(f"Resume file not found at {resume_path}")