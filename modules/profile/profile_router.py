import os

from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from modules.profile.models import User, UserProfile
from shared.schemas import UserProfileResponse
from core.security import MalwareScanner
import shutil

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: str):
    """
    Endpoint for retrieving user profiles with masked PII.
    """
    user = await User.get_or_none(id=user_id).prefetch_related("profile")

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Preparing data for Pydantic
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
    temp_file = f"storage/temp_{file.filename}"

    # Save file temporarily
    with open(temp_file, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # Trigger VirusTotal Scan
        await scanner.verify_file_safety(temp_file)
        return {"status": "clean", "filename": file.filename}
    finally:
        if os.path.exists(temp_file):
            os.remove(temp_file)
