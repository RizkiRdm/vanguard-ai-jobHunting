import uuid
from tortoise.transactions import in_transaction
from modules.agent.models import AgentTask, TaskStatus


async def claim_next_task() -> AgentTask | None:
    """
    Claims the next available task using Pessimistic Locking (FOR UPDATE).
    Ensures no double-processing in a concurrent environment.
    """
    async with in_transaction() as conn:
        # SQL: SELECT ... FOR UPDATE SKIP LOCKED
        # 'SKIP LOCKED' allows other workers to immediately skip this row
        # and look for the next available task instead of waiting.
        task = (
            await AgentTask.filter(status=TaskStatus.QUEUED)
            .order_by("created_at")
            .limit(1)
            .select_for_update(skip_locked=True)
            .get_or_none()
        )

        if task:
            task.status = TaskStatus.RUNNING
            await task.save(using_db=conn)
            return task

    return None


async def update_task_status(task_id: uuid.UUID, status: TaskStatus, error: str = None):
    """Updates the final state of the task."""
    task = await AgentTask.get(id=task_id)
    task.status = status
    if error:
        task.error_log = error
    await task.save()
