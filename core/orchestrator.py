import os
import uuid
from pathlib import Path
from contextlib import suppress

from fastapi import UploadFile
from tortoise.exceptions import OperationalError

from core.scraper import JobScraper
from core.security import MalwareScanner
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status
from core.custom_logging import logger
from modules.agent.models import AgentTask, TaskStatus
from modules.generator.services import generate_tailored_document


class JobOrchestrator:
    def __init__(self):
        self.scanner = MalwareScanner()
        self.ai = VanguardAI()
        self.browser = BrowserManager(headless=True)
        self.log = logger.bind(service="orchestrator")
        self.storage_path = Path("storage")
        self.storage_path.mkdir(exist_ok=True)
        self.scraper = JobScraper()

    async def execute_from_worker(
        self, task_id: str, user_id: str, task_type: str, bound_logger=None
    ):
        """
        Main entry point for the background worker to execute specific task types.
        Handles Discovery (Scraping) and Tailoring (Document Generation).
        """
        log = bound_logger or self.log
        log.info("worker_orchestration_started", task_type=task_type)

        # Use the Async Context Manager from BrowserManager as defined in browser.py
        async with self.browser.get_context() as context:
            page = await context.new_page()

            if task_type == "DISCOVERY":
                log.info("executing_discovery_logic")
                # TODO: Retrieve target_url from task metadata in production
                target_url = "https://www.linkedin.com/jobs/view/12345"

                try:
                    await page.goto(target_url, wait_until="networkidle")
                    # Trigger LLM-driven scraping
                    result = await self.scraper.scrape_llm(page, user_id)
                    return result
                except Exception as e:
                    log.error("discovery_failed", error=str(e))
                    raise e

            elif task_type == "TAILORING":
                log.info("executing_tailoring_logic")
                # Example context, should be fetched from ScrapedJob table in real flow
                job_context = "Software Engineer position at TechCorp"

                try:
                    result = await generate_tailored_document(
                        user_id, task_id, job_context
                    )
                    return result
                except Exception as e:
                    log.error("tailoring_failed", error=str(e))
                    raise e

            else:
                log.warning("unknown_task_type", task_type=task_type)
                return None

    async def run_full_pipeline(
        self, user_id: str, upload_file: UploadFile, target_url: str
    ):
        """
        Legacy/Synchronous entry point for immediate API processing.
        Usually followed by manual upload and scan.
        """
        task_id = str(uuid.uuid4())
        temp_file = self.storage_path / f"temp_{task_id}_{upload_file.filename}"

        self.log.info("sync_pipeline_started", user_id=user_id, task_id=task_id)

        try:
            # 1. Security validation
            content = await upload_file.read()
            temp_file.write_bytes(content)
            await self.scanner.verify_file_safety(str(temp_file))

            # 2. Persist initial task state
            await AgentTask.create(
                id=task_id,
                user_id=user_id,
                task_type="DISCOVERY",
                status=TaskStatus.RUNNING,
            )

            # 3. Execute logic immediately (Synchronous API behavior)
            return await self.execute_from_worker(task_id, user_id, "DISCOVERY")

        except Exception as e:
            self.log.error("sync_pipeline_failed", error=str(e))
            await update_task_status(task_id, TaskStatus.FAILED, error=str(e))
            raise e
        finally:
            # Cleanup temp file
            with suppress(FileNotFoundError):
                os.remove(temp_file)

    async def update_user_profile_safe(self, user_id: str, data: dict, log=None):
        """
        Updates user profile using Optimistic Locking to prevent race conditions.
        Ensures data integrity during concurrent updates.
        """
        from modules.profile.models import User, UserProfile

        log = log or self.log

        # 1. Fetch User to verify current version
        user = await User.get(id=user_id)
        current_version = user.version

        # 2. Increment version using atomic update filter (Optimistic Locking)
        updated_rows = await User.filter(id=user_id, version=current_version).update(
            version=current_version + 1
        )

        if not updated_rows:
            log.error("optimistic_lock_conflict", user_id=user_id)
            raise OperationalError(
                "Version mismatch: Profile was modified by another process."
            )

        # 3. Persist metadata to UserProfile table
        await UserProfile.update_or_create(user_id=user_id, defaults=data)

        log.info(
            "profile_update_complete",
            user_id=user_id,
            new_version=current_version + 1,
        )
        return {"status": "updated"}
