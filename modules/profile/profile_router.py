import os
import uuid
import shutil
from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends

from modules.agent.models import AgentTask, TaskStatus
from modules.profile.models import User
from shared.schemas import UserProfileResponse
from core.security import MalwareScanner
from core.custom_logging import logger

router = APIRouter(prefix="/profile", tags=["Profile"])
STORAGE_DIR = Path("storage")
STORAGE_DIR.mkdir(exist_ok=True)


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: str):
    """
    Retrieves user profile data with masked PII.
    """
    user = await User.get_or_none(id=user_id).prefetch_related("profile")

    if not user:
        logger.error("profile_not_found", user_id=user_id)
        raise HTTPException(status_code=404, detail="User not found")

    # Map database models to Pydantic response schema
    return {
        "id": str(user.id),
        "email": user.email,
        "target_role": user.profile.target_role if user.profile else None,
        "summary": user.profile.summary if user.profile else None,
    }


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...), scanner: MalwareScanner = Depends()
):
    """
    Performs immediate security validation on uploaded resumes.
    """
    temp_path = STORAGE_DIR / f"validation_{uuid.uuid4()}_{file.filename}"

    # Use context manager for safe file writing
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Blueprint Sec 2: Malware Scanning via VirusTotal
        await scanner.verify_file_safety(str(temp_path))
        return {"status": "clean", "filename": file.filename}
    finally:
        # Ensure temporary file is always removed
        if temp_path.exists():
            temp_path.unlink()


@router.post("/process-pipeline")
async def trigger_pipeline(
    user_id: str, file: UploadFile = File(...), scanner: MalwareScanner = Depends()
):
    """
    Main entry point for the job application pipeline.
    Validates security and queues the task for the background worker.
    """
    task_id = str(uuid.uuid4())
    # Worker expects file names to follow this specific pattern
    file_path = STORAGE_DIR / f"temp_{task_id}.zip"

    # 1. Persist the uploaded file to disk
    content = await file.read()
    file_path.write_bytes(content)

    try:
        # 2. Security Check (Non-negotiable requirement)
        await scanner.verify_file_safety(str(file_path))

        # 3. Create Task Record with QUEUED status
        # This will be picked up by the worker loop using SKIP LOCKED
        await AgentTask.create(
            id=task_id, user_id=user_id, task_type="APPLYING", status=TaskStatus.QUEUED
        )

        logger.info("pipeline_task_queued", task_id=task_id, user_id=user_id)

        return {
            "status": "queued",
            "task_id": task_id,
            "detail": "File accepted. Background processing has started.",
        }

    except Exception as e:
        # Cleanup file if pre-queue validation fails
        if file_path.exists():
            file_path.unlink()
        logger.error("pipeline_trigger_failed", error=str(e), user_id=user_id)
        raise HTTPException(status_code=400, detail=str(e))
