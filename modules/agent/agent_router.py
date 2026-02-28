import uuid

from fastapi import APIRouter, Depends, Response
from core.security import get_current_user_from_cookie, create_access_token
from modules.agent.models import AgentTask, TaskStatus

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/login-test")
async def login_test(response: Response):
    """Sesuai Contract: JWT disimpan dalam httpOnly cookie"""
    token = create_access_token(data={"sub": "test_user_id"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set True di production dengan HTTPS
        samesite="lax",
    )
    return {"message": "Login successful"}


@router.post("/scrape")
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
