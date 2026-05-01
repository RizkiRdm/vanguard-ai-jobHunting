import asyncio
import random
import sys
import signal
from pathlib import Path

# Ensure the project root is in sys.path
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)


from core.orchestrator import JobOrchestrator
from core.task_manager import claim_next_task, update_task_status
from core.custom_logging import logger
from modules.agent.models import TaskStatus


class VanguardWorker:
    def __init__(self):
        self.log = logger.bind(service="worker")
        self.orchestrator = JobOrchestrator()
        self.is_running = True

    async def shutdown(self, sig, frame):
        """Safe shutdown handler for system signals."""
        self.log.info("shutdown_signal_received", signal=sig.name)
        self.is_running = False

    async def run(self):
        """Main worker loop with improved resilience."""
        self.log.info("worker_started", provider="postgresql_native_skip_locked")


        try:
            while self.is_running:
                # 1. Fetch next task
                task = await claim_next_task()

                if task:
                    worker_log = self.log.bind(
                        task_id=str(task.id),
                        user_id=str(task.user_id),
                        task_type=task.task_type,
                    )

                    worker_log.info("task_claimed")

                    try:
                        # 2. Execute with correct signature from refactored orchestrator
                        # We pass task_id so orchestrator can fetch metadata itself
                        await self.orchestrator.execute_from_worker(
                            task_id=str(task.id),
                            user_id=str(task.user_id),
                            task_type=task.task_type,
                        )

                        # 3. Finalize status
                        await update_task_status(task.id, TaskStatus.COMPLETED)
                        worker_log.info("task_completed_successfully")

                    except Exception as e:
                        worker_log.error("task_execution_failed", error=str(e))
                        await update_task_status(
                            task.id, TaskStatus.FAILED, error=str(e)
                        )

                    # Small jitter to prevent DB thundering herd
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                else:
                    # No tasks? Wait with backoff logic
                    await asyncio.sleep(2)

        except Exception as e:
            self.log.critical("worker_panic", error=str(e))
        finally:
            self.log.info("cleaning_up_resources")


async def main():
    worker = VanguardWorker()

    # Setup Signal Handling (Linux/Unix)
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(
            sig, lambda s=sig: asyncio.create_task(worker.shutdown(s, None))
        )

    await worker.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
