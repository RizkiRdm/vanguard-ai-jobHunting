import random
import asyncio
from pathlib import Path
from typing import Dict, Any, List

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
    ):
        """
        Entry point utama worker. Sekarang mendukung loading session dan task chaining.
        """
        log = bound_logger or self.log
        log.info("execution_started", task_type=task_type, task_id=task_id)

        # 1. Load context browser dengan session user (Anti-Logout)
        async with self.browser.get_context(user_id=user_id) as context:
            page = await context.new_page()

            try:
                if task_type == "DISCOVERY":
                    return await self._handle_discovery(page, task_id, user_id, log)

                elif task_type == "AUTOMATED_APPLY":
                    return await self._handle_automated_apply(
                        page, task_id, user_id, log
                    )

                else:
                    log.error("unknown_task_type", task_type=task_type)
                    return {"status": "error", "message": "Unknown task type"}

            except Exception as e:
                log.error("task_execution_failed", error=str(e))
                await update_task_status(task_id, TaskStatus.FAILED, error=str(e))
                raise e

    async def _handle_discovery(self, page, task_id, user_id, log):
        """
        Logic untuk mencari lowongan dan MEMECAHNYA menjadi sub-tasks.
        """
        log.info("running_discovery_flow")
        await page.goto("https://www.linkedin.com/jobs/", wait_until="networkidle")

        # Scrape 10 jobs
        scraped_jobs = await self.scraper.scrape_llm(page, user_id)

        # TASK CHAINING
        for job in scraped_jobs:
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

        log.info("discovery_complete_subtasks_created", count=len(scraped_jobs))
        return {"status": "success", "subtasks_created": len(scraped_jobs)}

    async def _handle_automated_apply(self, page, task_id, user_id, log):
        """
        Logic autonomous apply dengan penanganan Resume Tailoring & Form Filling.
        """
        task = await AgentTask.get(id=task_id)
        target_url = task.metadata.get("target_url")

        # 1. GENERATE TAILORED RESUME
        log.info("tailoring_resume_for_job", job=task.metadata.get("job_title"))
        tailored_doc = await generate_tailored_document(user_id, task.metadata)

        # 2. SAVE RESUME NATIVELY
        temp_resume_path = self.storage_path / f"resume_{task_id}.pdf"
        temp_resume_path.write_bytes(tailored_doc.content)  # Safe binary write

        try:
            # 3. START AUTONOMOUS LOOP
            await page.goto(target_url, wait_until="networkidle")

            result = await self.run_autonomous_loop(
                page, task_id, user_id, temp_resume_path, log
            )
            return result
        finally:
            # CLEANUP
            if temp_resume_path.exists():
                temp_resume_path.unlink()

    async def run_autonomous_loop(self, page, task_id, user_id, resume_path, log):
        """
        Looping AI untuk navigasi UI LinkedIn sampai Submit.
        """
        user_profile = await UserProfile.get(user_id=user_id)
        max_steps = 15

        for step in range(max_steps):
            # Capture UI state
            screenshot_path = await self.browser.take_screenshot(
                page, f"apply_{task_id}_step_{step}"
            )

            # AI Decision
            decision = await self.ai.analyze_screen(
                screenshot_path=screenshot_path,
                goal=f"Apply to this job using resume at {resume_path}. Profile: {user_profile.summary}",
                user_id=user_id,
            )

            action = decision.get("action")
            log.info("ai_step", step=step, action=action)

            if action == "COMPLETE":
                await update_task_status(task_id, TaskStatus.COMPLETED)
                return {"status": "success"}

            if action == "AWAIT_USER":
                # SAVE STATE
                await update_task_status(task_id, TaskStatus.AWAITING_USER)
                return {
                    "status": "waiting_for_user",
                    "reason": decision.get("question"),
                }

            if action == "UPLOAD":
                await page.set_input_files(decision.get("selector"), str(resume_path))
                continue

            # Execute physical action (Click/Type)
            await self._perform_action(page, decision)
            await asyncio.sleep(random.uniform(1.0, 3.0))  # Anti-bot delay

        return {"status": "failed", "reason": "Max steps exceeded"}

    async def _perform_action(self, page, decision: Dict[str, Any]):
        selector = decision.get("selector")
        act_type = decision.get("action")
        value = decision.get("value")

        if act_type == "CLICK":
            await page.click(selector, timeout=5000)
        elif act_type == "TYPE":
            await page.fill(selector, str(value))
        elif act_type == "SELECT":
            await page.select_option(selector, value=str(value))
