import uuid
import json
from sqlalchemy import select, update, text
from core.database import AsyncSessionLocal
from modules.agent.models import AgentTask, TaskStatus


async def claim_next_task() -> AgentTask | None:
    """
    Claims the next available task using Pessimistic Locking (FOR UPDATE).
    Ensures no double-processing in a concurrent environment.
    """
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # Finding parents that are NOT completed
            active_parents_stmt = select(AgentTask.id).where(
                AgentTask.status.in_([TaskStatus.QUEUED, TaskStatus.RUNNING, TaskStatus.AWAIT_USER])
            )

            # SELECT FOR UPDATE SKIP LOCKED
            stmt = (
                select(AgentTask)
                .where(
                    AgentTask.status == TaskStatus.QUEUED,
                    ~AgentTask.parent_id.in_(active_parents_stmt)
                )
                .order_by(AgentTask.created_at)
                .limit(1)
                .with_for_update(skip_locked=True)
            )

            result = await session.execute(stmt)
            task = result.scalar_one_or_none()

            if task:
                task.status = TaskStatus.RUNNING
                # session.begin() will commit automatically
                return task

    return None


async def create_sub_task(
    parent_task_id: str, user_id: str, task_type: str, metadata: dict
) -> AgentTask:
    """Creates a new sub-task linked to a parent task."""
    async with AsyncSessionLocal() as session:
        task = AgentTask(
            id=uuid.uuid4(),
            parent_id=uuid.UUID(parent_task_id) if parent_task_id else None,
            user_id=uuid.UUID(user_id),
            task_type=task_type,
            status=TaskStatus.QUEUED,
            meta_data=metadata,
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


async def update_task_status(
    task_id: uuid.UUID | str, status: TaskStatus, error: str = None
):
    """Updates the final state of the task and notifies WebSocket listeners."""
    async with AsyncSessionLocal() as session:
        stmt = select(AgentTask).where(AgentTask.id == uuid.UUID(str(task_id)))
        result = await session.execute(stmt)
        task = result.scalar_one_or_none()
        
        if task:
            task.status = status
            if error:
                task.error_log = error
            await session.commit()
            
            # Notify task_updates
            notify_payload = {
                "task_id": str(task.id),
                "status": status.value,
                "user_id": str(task.user_id)
            }
            await session.execute(
                text("SELECT pg_notify('task_updates', :payload)"),
                {"payload": json.dumps(notify_payload)}
            )
