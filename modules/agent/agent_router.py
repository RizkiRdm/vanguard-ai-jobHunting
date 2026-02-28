import uuid
<<<<<<< HEAD
from typing import Dict, Any
from fastapi import APIRouter, Depends, Response, HTTPException
from fastapi.responses import FileResponse
from core.security import get_current_user_from_cookie, create_access_token
from core.browser import BrowserManager
from modules.agent.models import AgentTask, TaskStatus, LLMUsageLog
from core.custom_logging import logger
=======

from fastapi import APIRouter, Depends, Response
from core.security import get_current_user_from_cookie, create_access_token
from modules.agent.models import AgentTask, TaskStatus
>>>>>>> 8a68e69 (refactor(core): improve scraping reliability and mock stability)

router = APIRouter(prefix="/agent", tags=["Agent Automation"])
log = logger.bind(service="agent_router")


@router.post("/login")
async def login(response: Response, user_id: str = "admin-user"):
    """Authenticates user and sets an HttpOnly JWT cookie."""
    token = create_access_token(data={"sub": user_id})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return {"status": "success", "user_id": user_id}


@router.get("/session-login")
async def capture_session(user_id: str = Depends(get_current_user_from_cookie)):
    """Opens a headful browser for manual login to capture session cookies."""
    browser_mgr = BrowserManager(headless=False)
    try:
        async with browser_mgr.get_context(user_id=user_id) as context:
            page = await context.new_page()
            await page.goto("https://www.linkedin.com/login")
            # Wait for user to login manually and close browser
            await page.wait_for_timeout(120000)
        return {"status": "session_saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape")
<<<<<<< HEAD
async def trigger_discovery(
    target_url: str, user_id: str = Depends(get_current_user_from_cookie)
):
    """Queues a new job discovery task."""
    task_id = str(uuid.uuid4())
    await AgentTask.create(
        id=task_id,
        user_id=user_id,
        task_type="DISCOVERY",
        status=TaskStatus.QUEUED,
        metadata={"target_url": target_url},
    )
    return {"task_id": task_id, "status": "queued"}


@router.get("/tasks")
async def list_tasks(user_id: str = Depends(get_current_user_from_cookie)):
    """Retrieves all tasks associated with the current user."""
    tasks = await AgentTask.filter(user_id=user_id).order_by("-created_at")
    return tasks


@router.post("/interact/{task_id}")
async def human_interaction(
    task_id: str,
    answer: Dict[str, Any],
    user_id: str = Depends(get_current_user_from_cookie),
):
    """Provides answers to the AI when it encounters a roadblock (AWAIT_USER)."""
    task = await AgentTask.get_or_none(id=task_id, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.metadata["user_answer"] = answer
    task.status = TaskStatus.QUEUED  # Re-queue to resume
    await task.save()
    return {"status": "resumed"}


@router.get("/tasks/{task_id}/screenshot")
async def get_task_screenshot(
    task_id: str, user_id: str = Depends(get_current_user_from_cookie)
):
    """Returns the latest screenshot taken by the bot for visual debugging."""
    task = await AgentTask.get_or_none(id=task_id, user_id=user_id)
    if not task or "last_screenshot" not in task.metadata:
        raise HTTPException(status_code=404, detail="No screenshot available")

    return FileResponse(task.metadata["last_screenshot"])


@router.post("/tasks/{task_id}/stop")
async def stop_task(task_id: str, user_id: str = Depends(get_current_user_from_cookie)):
    """Forcibly cancels a running or queued task."""
    task = await AgentTask.get_or_none(id=task_id, user_id=user_id)
    if task:
        task.status = TaskStatus.FAILED
        task.error = "Cancelled by user"
        await task.save()
    return {"status": "stopped"}
=======
async def scrape_web(
    target_url: str, user_id: str = Depends(get_current_user_from_cookie)
):
    task_id = str(uuid.uuid4())

    # Masukkan ke antrean task (DISCOVERY)
    await AgentTask.create(
        id=task_id, user_id=user_id, task_type="DISCOVERY", status=TaskStatus.QUEUED
    )

    return {
        "status": "queued",
        "task_id": task_id,
        "message": "Scraping task initiated via Gemini AI.",
    }
>>>>>>> 8a68e69 (refactor(core): improve scraping reliability and mock stability)
