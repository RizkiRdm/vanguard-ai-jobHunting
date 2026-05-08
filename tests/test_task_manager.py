import pytest
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from modules.agent.models import AgentTask, TaskStatus
from core.task_manager import claim_next_task

@pytest.mark.asyncio
async def test_claim_next_task_concurrency(db_session: AsyncSession):
    # Setup: Create 2 tasks
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    task1 = AgentTask(user_id=uuid.UUID(user_id), task_type="DISCOVERY", status=TaskStatus.QUEUED.value)
    task2 = AgentTask(user_id=uuid.UUID(user_id), task_type="DISCOVERY", status=TaskStatus.QUEUED.value)
    db_session.add_all([task1, task2])
    await db_session.commit()

    # Attempt to claim tasks concurrently
    task_claim1 = await claim_next_task(db_session)
    task_claim2 = await claim_next_task(db_session)

    assert task_claim1 is not None
    assert task_claim2 is not None
    assert task_claim1.id != task_claim2.id
