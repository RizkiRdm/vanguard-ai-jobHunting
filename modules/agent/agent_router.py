import uuid
from typing import Dict, Any
from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.responses import FileResponse
from core.security import get_current_user_from_cookie, create_access_token
from core.websocket_manager import manager
from modules.agent.models import AgentTask, TaskStatus
from core.custom_logging import logger

router = APIRouter(prefix="/agent", tags=["Agent Automation"])
log = logger.bind(service="agent_router")


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Real-time stream connection for frontend."""
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Tetap terbuka, biarkan manager yang mengirim pesan dari orchestrator
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@router.post("/login-test")
async def login_test(response: Response):
    token = create_access_token(data={"sub": "test-user"})
    response.set_cookie(
        key="access_token", value=token, httponly=True, secure=True, samesite="lax"
    )
    return {"status": "success"}


@router.post("/login")
async def login(response: Response, user_id: str = "admin-user"):
    token = create_access_token(data={"sub": user_id})
    response.set_cookie(
        key="access_token", value=token, httponly=True, secure=True, samesite="lax"
    )
    return {"status": "success", "user_id": user_id}


@router.post("/scrape")
async def trigger_discovery(user_id: str = Depends(get_current_user_from_cookie)):
    """Memicu Google Dorking task."""
    task_id = str(uuid.uuid4())
    await AgentTask.create(
        id=task_id,
        user_id=user_id,
        task_type="DISCOVERY",
        status=TaskStatus.QUEUED,
        metadata={"mode": "dorking"},
    )
    return {"task_id": task_id, "status": "queued"}


@router.get("/tasks")
async def list_tasks(user_id: str = Depends(get_current_user_from_cookie)):
    return await AgentTask.filter(user_id=user_id).order_by("-created_at")


@router.post("/interact/{task_id}")
async def human_interaction(
    task_id: str,
    answer: Dict[str, Any],
    user_id: str = Depends(get_current_user_from_cookie),
):
    task = await AgentTask.get_or_none(id=task_id, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.metadata["user_answer"] = answer
    task.status = TaskStatus.QUEUED
    await task.save()
    return {"status": "resumed"}


@router.get("/tasks/{task_id}/screenshot")
async def get_task_screenshot(
    task_id: str, user_id: str = Depends(get_current_user_from_cookie)
):
    task = await AgentTask.get_or_none(id=task_id, user_id=user_id)
    if not task or "last_screenshot" not in task.metadata:
        raise HTTPException(status_code=404, detail="No screenshot available")
    return FileResponse(task.metadata["last_screenshot"])


@router.post("/tasks/{task_id}/stop")
async def stop_task(task_id: str, user_id: str = Depends(get_current_user_from_cookie)):
    task = await AgentTask.get_or_none(id=task_id, user_id=user_id)
    if task:
        task.status = TaskStatus.FAILED
        task.metadata["error"] = "Cancelled by user"
        await task.save()
    return {"status": "stopped"}
