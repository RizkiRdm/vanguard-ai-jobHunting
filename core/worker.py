import asyncio
from pathlib import Path
import sys
from tortoise import Tortoise

# Ensure the project root is in sys.path for module resolution
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

from core.database import TORTOISE_CONFIG
from core.orchestrator import JobOrchestrator
from core.task_manager import claim_next_task, update_task_status
from core.custom_logging import logger
from modules.agent.models import TaskStatus


async def worker_loop():
    """
    Lightweight Worker using PostgreSQL 'SKIP LOCKED'.
    Compliant with local-spec requirements: No Redis, No TaskIQ.
    """
    log = logger.bind(service="worker")
    log.info("worker_started", provider="postgresql_native")

    # Initialize Database Connection
    await Tortoise.init(config=TORTOISE_CONFIG)
    orchestrator = JobOrchestrator()

    try:
        while True:
            # Claim task using Pessimistic Locking (FOR UPDATE SKIP LOCKED)
            task = await claim_next_task()

            if task:
                # Create a bound logger to trace this specific task across modules
                worker_log = logger.bind(
                    task_id=str(task.id),
                    user_id=str(task.user_id),
                    attempt=getattr(task, "retry_count", 0),
                )

                worker_log.info("task_processing_start")

                try:
                    # Execute orchestrator logic
                    # File path follows the pattern established in the router
                    file_path = f"storage/temp_{task.id}.zip"

                    await orchestrator.execute_from_worker(
                        user_id=str(task.user_id),
                        file_path=file_path,
                        target_url="https://linkedin.com",
                        bound_logger=worker_log,
                    )

                    # Mark task as completed in DB
                    await update_task_status(task.id, TaskStatus.COMPLETED)
                    worker_log.info("task_processing_success")

                except Exception as e:
                    worker_log.error("task_processing_failed", error=str(e))
                    await update_task_status(task.id, TaskStatus.FAILED, error=str(e))
            else:
                # Idle wait to reduce CPU/DB load when queue is empty
                await asyncio.sleep(5)

    except asyncio.CancelledError:
        log.info("worker_received_shutdown_signal")
    finally:
        log.info("worker_cleaning_up_connections")
        await Tortoise.close_connections()


if __name__ == "__main__":
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        pass
