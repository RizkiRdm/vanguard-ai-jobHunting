import os
import uuid
from pathlib import Path
from contextlib import suppress

from fastapi import UploadFile
from tortoise.exceptions import OperationalError

from core.security import MalwareScanner
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status
from core.custom_logging import logger
from modules.agent.models import AgentTask, TaskStatus


class JobOrchestrator:
    def __init__(self):
        self.scanner = MalwareScanner()
        self.ai = VanguardAI()
        self.browser = BrowserManager(headless=True)
        self.log = logger.bind(service="orchestrator")
        self.storage_path = Path("storage")
        self.storage_path.mkdir(exist_ok=True)

    async def run_full_pipeline(
        self, user_id: str, upload_file: UploadFile, target_url: str
    ):
        """Main entry point for synchronous API flow."""
        task_id = str(uuid.uuid4())
        temp_file = self.storage_path / f"temp_{task_id}_{upload_file.filename}"

        self.log.info("pipeline_started", user_id=user_id, task_id=task_id)

        try:
            # 1. Security validation
            content = await upload_file.read()
            temp_file.write_bytes(content)
            await self.scanner.verify_file_safety(str(temp_file))

            # 2. Persist initial task state
            task = await AgentTask.create(
                id=task_id,
                user_id=user_id,
                task_type="APPLYING",
                status=TaskStatus.RUNNING,
            )

            # 3. Browser & AI Execution
            async with self.browser.get_context() as context:
                page = await context.new_page()
                await page.goto(target_url)

                ss_path = self.storage_path / f"ss_{task_id}.png"
                await page.screenshot(path=str(ss_path))

                decision = await self.ai.analyze_screen(
                    str(ss_path), goal=f"Apply for job at {target_url}", user_id=user_id
                )

                # 4. Finalize Task Status
                new_status = (
                    TaskStatus.COMPLETED
                    if decision.get("action") == "complete"
                    else TaskStatus.FAILED
                )
                await update_task_status(
                    task.id, new_status, error=decision.get("reasoning")
                )

                with suppress(FileNotFoundError):
                    ss_path.unlink()

            return {"status": "success", "task_id": task_id}

        except Exception as e:
            self.log.error("pipeline_execution_failed", error=str(e))
            if "task" in locals():
                await update_task_status(task.id, TaskStatus.FAILED, error=str(e))
            raise e

        finally:
            with suppress(FileNotFoundError):
                temp_file.unlink()

    async def execute_from_worker(
        self, user_id: str, file_path: str, target_url: str, bound_logger=None
    ):
        """Wrapper for background worker execution logic."""
        log = bound_logger or self.log.bind(user_id=user_id)
        log.info("worker_orchestration_triggered")

        # Placeholder for real browser logic
        # In the future, this would call analyze_screen and browser actions

        return await self.update_user_profile_safe(
            user_id,
            {"summary": "Profile successfully processed via background worker"},
            log=log,
        )

    async def update_user_profile_safe(self, user_id: str, data: dict, log=None):
        """
        Updates user profile using Optimistic Locking.
        Compliant with Blueprint Section 6.
        """
        from modules.profile.models import User, UserProfile

        log = log or self.log

        # 1. Fetch User to verify current version
        user = await User.get(id=user_id)
        current_version = user.version

        # 2. Increment version using atomic update filter
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
