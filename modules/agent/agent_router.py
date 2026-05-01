import uuid
from uuid import UUID
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


from jose import jwt, JWTError
from fastapi import (
    APIRouter,
    Depends,
    Response,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    Query,
)

# ... (other imports)
from core.security import JWT_SECRET_KEY, ALGORITHM

# ...

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    user_id: str, 
    token: str = Query(...)
):
    """Real-time stream connection with JWT handshake."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("sub") != user_id:
            raise HTTPException(status_code=403)
    except (JWTError, HTTPException):
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
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


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db

@router.post("/scrape")
async def trigger_discovery(
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    """Memicu Google Dorking task."""
    task_id = uuid.uuid4()
    task = AgentTask(
        id=task_id,
        user_id=user_id,
        task_type="DISCOVERY",
        status=TaskStatus.QUEUED.value,
        metadata={"mode": "dorking"},
    )
    db.add(task)
    await db.commit()
    return {"task_id": task_id, "status": "queued"}


@router.get("/tasks")
async def list_tasks(
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AgentTask).filter_by(user_id=user_id).order_by(AgentTask.created_at.desc())
    )
    return result.scalars().all()


@router.post("/interact/{task_id}")
async def human_interaction(
    task_id: UUID,
    answer: Dict[str, Any],
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AgentTask).filter_by(id=task_id, user_id=user_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.meta_data["user_answer"] = answer
    task.status = TaskStatus.QUEUED.value
    await db.commit()
    return {"status": "resumed"}


@router.get("/tasks/{task_id}/screenshot")
async def get_task_screenshot(
    task_id: UUID, 
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AgentTask).filter_by(id=task_id, user_id=user_id))
    task = result.scalar_one_or_none()
    if not task or "last_screenshot" not in task.meta_data:
        raise HTTPException(status_code=404, detail="No screenshot available")
    return FileResponse(task.meta_data["last_screenshot"])


@router.post("/tasks/{task_id}/stop")
async def stop_task(
    task_id: UUID, 
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(AgentTask).filter_by(id=task_id, user_id=user_id))
    task = result.scalar_one_or_none()
    if task:
        task.status = TaskStatus.FAILED.value
        task.meta_data["error"] = "Cancelled by user"
        await db.commit()
    return {"status": "stopped"}
