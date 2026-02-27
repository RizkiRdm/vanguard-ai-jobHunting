import pytest
import uuid
from modules.agent.models import AgentTask, TaskStatus
from core.task_manager import claim_next_task
from core.worker import worker_loop
import asyncio

from modules.profile.models import User


@pytest.mark.asyncio
async def test_worker_can_claim_and_process_task():
    test_user = await User.create(email=f"test_{uuid.uuid4().hex[:6]}@example.com")
    # 1. SETUP: Buat task manual di DB dengan status QUEUED
    task_id = uuid.uuid4()
    task = await AgentTask.create(
        id=task_id,
        user_id=str(test_user.id),  # Mengambil ID dari User yang baru dibuat
        task_type="APPLYING",
        status=TaskStatus.QUEUED,
    )

    # 2. TEST CLAIM: Pastikan logic SKIP LOCKED bekerja
    claimed_task = await claim_next_task()

    assert claimed_task is not None
    assert claimed_task.id == task.id
    assert claimed_task.status == TaskStatus.RUNNING

    # 3. VERIFIKASI DB: Pastikan status di DB juga terupdate
    db_task = await AgentTask.get(id=task.id)
    assert db_task.status == TaskStatus.RUNNING
