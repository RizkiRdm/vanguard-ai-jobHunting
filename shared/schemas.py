from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


# --- USER SCHEMAS ---
class UserBase(BaseModel):
    """Base schema for User data"""

    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """Schema for creating a new user (Registration)"""

    password: str


class User(UserBase):
    """Full User schema for internal/response use"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- PROFILE SCHEMAS ---


class ProfileBase(BaseModel):
    """Base schema for User Profile (CV Header)"""

    summary: Optional[str] = None
    target_role: Optional[str] = None


class ProfileCreate(ProfileBase):
    user_id: UUID


class Profile(ProfileBase):
    id: UUID
    user_id: UUID
    last_parsed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- TASK & AGENT SCHEMAS ---


class TaskBase(BaseModel):
    """Base schema for Agent Tasks"""

    target_url: str
    portal_id: Optional[UUID] = None


class TaskCreate(TaskBase):
    user_id: UUID


class Task(TaskBase):
    id: UUID
    user_id: UUID
    status: str = "QUEUED"  # QUEUED, RUNNING, COMPLETED, FAILED, STOPPED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExecutionLog(BaseModel):
    """Schema for real-time agent activity logs"""

    id: int
    task_id: UUID
    level: str
    message: str
    screenshot_path: Optional[str] = None
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)
