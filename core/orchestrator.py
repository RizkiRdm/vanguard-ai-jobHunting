import os
import uuid
from fastapi import UploadFile
from core.security import MalwareScanner
from core.ai_agent import VanguardAI
from core.browser import BrowserManager
from core.task_manager import update_task_status
from modules.agent.models import AgentTask, TaskStatus
from core.logging import logger


class JobOrchestrator:
    def __init__(self):
        self.scanner = MalwareScanner()
        self.ai = VanguardAI()
        self.browser = BrowserManager(headless=True)
        self.log = logger.bind(service="orchestrator")

    async def run_full_pipeline(
        self, user_id: str, upload_file: UploadFile, target_url: str
    ):
        task_id = str(uuid.uuid4())
        # Pastikan folder storage ada
        os.makedirs("storage", exist_ok=True)
        temp_path = f"storage/temp_{task_id}_{upload_file.filename}"

        self.log.info("pipeline_started", user_id=user_id, task_id=task_id)

        try:
            # 1. Malware Scan
            with open(temp_path, "wb") as f:
                f.write(await upload_file.read())

            await self.scanner.verify_file_safety(temp_path)
            self.log.info("security_scan_passed")

            # 2. Create Task in DB
            task = await AgentTask.create(
                id=task_id,
                user_id=user_id,
                task_type="APPLYING",
                status=TaskStatus.RUNNING,
            )

            # 3. AI & Browser Execution
            async with self.browser.get_context() as context:
                page = await context.new_page()
                await page.goto(target_url)

                # Ambil screenshot untuk AI
                screenshot_path = f"storage/ss_{task_id}.png"
                await page.screenshot(path=screenshot_path)

                # AI Decision (Sekarang memanggil Gemini asli/mocked via conftest)
                decision = await self.ai.analyze_screen(
                    screenshot_path,
                    goal=f"Apply for job at {target_url}",
                    user_id=user_id,
                )

                # Update Status berdasarkan keputusan AI
                if decision["action"] == "complete":
                    await update_task_status(task.id, TaskStatus.COMPLETED)
                    self.log.info("pipeline_completed", task_id=task_id)
                else:
                    await update_task_status(
                        task.id, TaskStatus.FAILED, error=decision.get("reasoning")
                    )

                # Cleanup screenshot
                if os.path.exists(screenshot_path):
                    os.remove(screenshot_path)

            return {"status": "success", "task_id": task_id}

        except Exception as e:
            self.log.error("pipeline_failed", error=str(e))
            # Jika task sudah sempat dibuat di DB, update statusnya ke FAILED
            if "task" in locals():
                await update_task_status(task.id, TaskStatus.FAILED, error=str(e))
            raise e

        finally:
            # Cleanup file upload sementara
            if os.path.exists(temp_path):
                os.remove(temp_path)
