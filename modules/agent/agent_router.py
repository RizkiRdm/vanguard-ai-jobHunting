import uuid
from fastapi import APIRouter, Depends, HTTPException
from core.security import get_current_user_from_cookie
from modules.agent.models import AgentTask, TaskStatus
from core.custom_logging import logger

router = APIRouter(prefix="/agent", tags=["Agent Automation"])
log = logger.bind(service="agent_core")


@router.post("/scrape")
async def start_discovery(
    target_url: str, user_id: str = Depends(get_current_user_from_cookie)
):
    task_id = str(uuid.uuid4())
    await AgentTask.create(
        id=task_id,
        user_id=user_id,
        task_type="DISCOVERY",
        status=TaskStatus.QUEUED,
        metadata={"target_url": target_url},
    )
    return {"task_id": task_id, "status": "queued"}


@router.post("/interact/{task_id}")
async def submit_answer(
    task_id: str, answer: dict, user_id: str = Depends(get_current_user_from_cookie)
):
    task = await AgentTask.get_or_none(id=task_id, user_id=user_id)
    if not task or task.status != TaskStatus.AWAITING_USER:
        raise HTTPException(status_code=400, detail="Task not awaiting interaction")

    task.metadata["human_answer"] = answer
    task.status = TaskStatus.QUEUED
    await task.save()
    return {"status": "resumed"}
