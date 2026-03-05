import uuid
from tortoise.transactions import in_transaction
from modules.agent.models import AgentTask, TaskStatus


async def claim_next_task() -> AgentTask | None:
    """
    Claims the next available task using Pessimistic Locking (FOR UPDATE).
    Ensures no double-processing in a concurrent environment.
    """
    async with in_transaction() as conn:
        # Finding parents that are NOT completed
        active_parents = await AgentTask.filter(
            status__in=[TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.AWAITING_USER]
        ).values_list("id", flat=True)

        task = (
            await AgentTask.filter(status=TaskStatus.QUEUED)
            .exclude(parent_id__in=active_parents)
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


async def create_sub_task(
    parent_task_id: str, user_id: str, task_type: str, metadata: dict
) -> AgentTask:
    """Creates a new sub-task linked to a parent task."""
    task = await AgentTask.create(
        id=uuid.uuid4(),
        parent_id=parent_task_id,
        user_id=user_id,
        task_type=task_type,
        status=TaskStatus.QUEUED,
        metadata=metadata,
    )
    return task


async def update_task_status(
    task_id: uuid.UUID | str, status: TaskStatus, error: str = None
):
    """Updates the final state of the task."""
    task = await AgentTask.get(id=task_id)
    task.status = status
    if error:
        task.error_log = error
    await task.save()
