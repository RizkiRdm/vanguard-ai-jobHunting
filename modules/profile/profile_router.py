import uuid
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from tortoise.functions import Sum

from modules.agent.models import AgentTask, TaskStatus, LLMUsageLog
from core.security import MalwareScanner, get_current_user_from_cookie
from core.custom_logging import logger

router = APIRouter(prefix="/profile", tags=["User Profile"])
RESUME_DIR = Path("storage/resumes")
RESUME_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/process-resume")
async def upload_resume_and_apply(
    file: UploadFile = File(...),
    scanner: MalwareScanner = Depends(),
    user_id: str = Depends(get_current_user_from_cookie),
):
    """Uploads resume, performs safety scan, and triggers auto-apply task."""
    task_id = str(uuid.uuid4())
    safe_name = f"{user_id}_{task_id}{Path(file.filename).suffix}"
    file_path = RESUME_DIR / safe_name

    try:
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        await scanner.verify_file_safety(str(file_path))

        await AgentTask.create(
            id=task_id,
            user_id=user_id,
            task_type="APPLYING",
            status=TaskStatus.QUEUED,
            metadata={"resume_path": str(file_path)},
        )
        return {"task_id": task_id, "status": "queued"}

    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        logger.error("upload_pipeline_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/stats")
async def get_bot_statistics(user_id: str = Depends(get_current_user_from_cookie)):
    """Calculates bot performance and AI cost efficiency for the user."""
    total_applied = await AgentTask.filter(
        user_id=user_id, status=TaskStatus.COMPLETED, task_type="APPLYING"
    ).count()

    usage = (
        await LLMUsageLog.filter(user_id=user_id)
        .annotate(total_tokens=Sum("total_tokens"))
        .first()
    )

    return {
        "total_applications": total_applied,
        "total_ai_tokens_used": usage.total_tokens if usage else 0,
        "active_tasks": await AgentTask.filter(
            user_id=user_id, status=TaskStatus.RUNNING
        ).count(),
    }
