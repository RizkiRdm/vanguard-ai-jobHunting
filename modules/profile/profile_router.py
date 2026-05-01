import os
import json
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_current_user_from_cookie
from modules.profile.models import UserProfile
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/profile", tags=["User Profile"])

class ProfileUpdateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    target_role: Optional[str] = None
    expected_salary: Optional[str] = None
    summary: Optional[str] = None
    skills: Optional[List[str]] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None

@router.get("/me")
async def get_my_profile(
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(UserProfile).filter_by(user_id=user_id))
        profile = result.scalar_one_or_none()
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Convert skills back to list for response if needed
        if profile.skills:
            profile.skills = profile.skills.split(",")
        else:
            profile.skills = []
            
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_profile_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/me")
async def update_my_profile(
    data: ProfileUpdateSchema, 
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(UserProfile).filter_by(user_id=user_id))
        profile = result.scalar_one_or_none()
        
        update_data = data.model_dump(exclude_unset=True)
        if "skills" in update_data and update_data["skills"]:
            update_data["skills"] = ",".join(update_data["skills"])

        if not profile:
            profile = UserProfile(user_id=user_id, **update_data)
            db.add(profile)
        else:
            for key, value in update_data.items():
                setattr(profile, key, value)
        
        await db.commit()
        await db.refresh(profile)
        
        # Convert skills back for response
        if profile.skills:
            profile.skills = profile.skills.split(",")
        else:
            profile.skills = []
            
        return {"status": "success", "message": "Profile updated", "data": profile}
    except Exception as e:
        await db.rollback()
        logger.error("update_profile_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...), 
    user_id: str = Depends(get_current_user_from_cookie),
    db: AsyncSession = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files allowed")

    try:
        # Ensure storage directory exists
        os.makedirs("storage/resumes", exist_ok=True)
        
        file_path = f"storage/resumes/{user_id}_resume.pdf"
        content = await file.read()
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        result = await db.execute(select(UserProfile).filter_by(user_id=user_id))
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = UserProfile(user_id=user_id, resume_url=file_path)
            db.add(profile)
        else:
            profile.resume_url = file_path
            
        await db.commit()
        return {"url": file_path}
    except Exception as e:
        await db.rollback()
        logger.error("upload_resume_failed", user_id=user_id, error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
