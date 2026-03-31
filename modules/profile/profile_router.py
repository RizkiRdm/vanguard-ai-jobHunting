import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from core.security import get_current_user_from_cookie
from modules.profile.models import UserProfile
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/profile", tags=["User Profile"])

class ProfileUpdateSchema(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    target_role: Optional[str]
    expected_salary: Optional[str]
    summary: Optional[str]
    skills: Optional[List[str]]
    experience_years: Optional[int]
    location: Optional[str]

@router.get("/me")
async def get_my_profile(user_id: str = Depends(get_current_user_from_cookie)):
    profile = await UserProfile.get_or_none(user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.put("/me")
async def update_my_profile(
    data: ProfileUpdateSchema, 
    user_id: str = Depends(get_current_user_from_cookie)
):
    profile = await UserProfile.get_or_none(user_id=user_id)
    if not profile:
        profile = await UserProfile.create(user_id=user_id, **data.dict(exclude_unset=True))
    else:
        await profile.update_from_dict(data.dict(exclude_unset=True)).save()
    
    return {"status": "success", "message": "Profile updated", "data": profile}

@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...), 
    user_id: str = Depends(get_current_user_from_cookie)
):
    # Ensure storage directory exists
    os.makedirs("storage/resumes", exist_ok=True)
    
    file_path = f"storage/resumes/{user_id}_resume.pdf"
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    profile = await UserProfile.get_or_none(user_id=user_id)
    if profile:
        profile.resume_url = file_path
        await profile.save()
        
    return {"url": file_path}