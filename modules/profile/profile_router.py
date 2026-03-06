import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, Response, HTTPException, UploadFile, File
from core.security import (
    get_current_user_from_cookie,
    create_access_token,
    get_password_hash,
    verify_password,
    GoogleAuthService,
    MalwareScanner,
)
from modules.profile.models import User, UserProfile
from modules.agent.models import AgentTask, TaskStatus
from core.custom_logging import logger

router = APIRouter(prefix="/profile", tags=["User Profile & Auth"])
STORAGE_DIR = Path("storage/resumes")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
# --- AUTHENTICATION ---


@router.post("/auth/google")
async def google_login(payload: dict, response: Response):
    """Google OAuth Sign-in/Sign-up."""
    auth_service = GoogleAuthService()
    user_info = await auth_service.verify_google_token(payload.get("token"))

    if not user_info:
        raise HTTPException(status_code=401, detail="Invalid Google Credentials")

    user, created = await User.get_or_create(
        email=user_info["email"],
        defaults={"id": uuid.uuid4(), "auth_provider": "GOOGLE"},
    )

    if created:
        await UserProfile.create(id=uuid.uuid4(), user=user)

    token = create_access_token(data={"sub": str(user.id)})
    response.set_cookie(key="access_token", value=token, httponly=True, samesite="lax")
    return {"status": "success", "user_id": user.id}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}


# --- DATA MANAGEMENT (Resume Upload) ---


@router.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...),
    scanner: MalwareScanner = Depends(),
    user_id: str = Depends(get_current_user_from_cookie),
):
    """
    Saves resume, scans for malware, and updates profile.
    """
    task_id = str(uuid.uuid4())
    file_extension = Path(file.filename).suffix
    # Gunakan UUID agar tidak terjadi path traversal atau nama file bentrok
    file_path = STORAGE_DIR / f"{user_id}_{task_id}{file_extension}"

    try:
        # 1. Simpan file sementara ke disk
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # 2. PENGGUNAAN SCANNER (CRUCIAL):
        # Ini akan mengecek hash file ke VirusTotal atau scanner lokal
        await scanner.verify_file_safety(str(file_path))

        # 3. Update User Profile
        profile = await UserProfile.get(user_id=user_id)
        profile.starter_cv_path = str(file_path)
        await profile.save()

        # 4. Trigger Task (Opsional: Jika ingin langsung apply setelah upload)
        await AgentTask.create(
            id=task_id,
            user_id=user_id,
            task_type="APPLYING",
            status=TaskStatus.QUEUED,
            metadata={"resume_path": str(file_path)},
        )

        logger.info(
            "resume_secured_and_profile_updated", user_id=user_id, task_id=task_id
        )
        return {"status": "success", "task_id": task_id, "path": str(file_path)}

    except HTTPException as he:
        # Jika malware terdeteksi (403), hapus file dan re-throw
        if file_path.exists():
            file_path.unlink()
        raise he
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        logger.error("upload_failed", error=str(e))
        raise HTTPException(
            status_code=500, detail="Internal server error during upload"
        )
