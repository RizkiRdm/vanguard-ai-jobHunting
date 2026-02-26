import pytest
import io
from fastapi import UploadFile
from modules.profile.models import User
from modules.agent.models import AgentTask, TaskStatus, LLMUsageLog
from core.orchestrator import JobOrchestrator


@pytest.mark.asyncio
async def test_full_pipeline_success():
    # Setup: Create real user in DB
    user = await User.create(email="e2e_tester@vanguard.ai")

    # Setup: Create dummy zip file
    zip_content = b"fake-zip-data"
    fake_file = UploadFile(filename="cv.zip", file=io.BytesIO(zip_content))

    orchestrator = JobOrchestrator()

    # Execute
    result = await orchestrator.run_full_pipeline(
        user_id=str(user.id),
        upload_file=fake_file,
        target_url="https://company.com/apply",
    )

    # Verification
    assert result["status"] == "success"

    # Check Task State
    updated_task = await AgentTask.get(id=result["task_id"])
    assert updated_task.status == TaskStatus.COMPLETED

    # Check Token Audit (Integration from VG-4.1)
    audit_log = await LLMUsageLog.filter(user_id=user.id).first()
    assert audit_log is not None
    assert audit_log.total_tokens == 150
