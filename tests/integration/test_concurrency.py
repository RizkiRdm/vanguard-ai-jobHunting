import asyncio
import pytest
from tortoise import Tortoise
from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import User
from core.task_manager import claim_next_task
from core.database import TORTOISE_CONFIG


@pytest.mark.asyncio(loop_scope="function")
async def test_pessimistic_locking_prevents_double_claim():
    """
    DoD: Running 2 workers concurrently does not cause double-processing.
    Verification: Confirms 'SELECT FOR UPDATE SKIP LOCKED' behavior.
    """
    # 1. Initialize Tortoise with explicit model registration
    # This ensures AgentTask and User are mapped to the 'default' connection
    await Tortoise.init(
        db_url=TORTOISE_CONFIG["connections"]["default"],
        modules={"models": ["modules.agent.models", "modules.profile.models"]},
    )
    await Tortoise.generate_schemas()

    try:
        # 2. Cleanup & Setup Test Data
        await AgentTask.all().delete()
        await User.all().delete()

        test_user = await User.create(
            username="concurrency_test_worker",
            email="worker_concurrency@test.com",
            auth_provider="LOCAL",
        )

        task = await AgentTask.create(
            user_id=test_user.id, task_type="APPLYING", status=TaskStatus.QUEUED
        )

        # 3. Simulate 2 workers claiming concurrently
        # Triggers SELECT FOR UPDATE SKIP LOCKED logic
        worker_1_result, worker_2_result = await asyncio.gather(
            claim_next_task(), claim_next_task()
        )

        # 4. Verification
        results = [worker_1_result, worker_2_result]
        claimed_tasks = [r for r in results if r is not None]

        # One worker claims it, the other gets None
        assert len(claimed_tasks) == 1, (
            f"Error: {len(claimed_tasks)} workers claimed the task."
        )
        assert claimed_tasks[0].id == task.id

        # Verify final state in DB
        updated_task = await AgentTask.get(id=task.id)
        assert updated_task.status == TaskStatus.RUNNING

        print("\n✅ Concurrency Check Passed: Locking handled correctly.")

    finally:
        # 5. Mandatory connection closure
        await Tortoise.close_connections()
