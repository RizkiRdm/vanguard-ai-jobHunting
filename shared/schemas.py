from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


# Standard Error Schema for consistency
class ErrorDetail(BaseModel):
    loc: List[str] = Field(..., example=["body", "file"])
    msg: str = Field(..., example="field required")
    type: str = Field(..., example="value_error.missing")


class ErrorResponse(BaseModel):
    detail: str = Field(..., example="User not found")


# Profile Schemas
class UserProfileResponse(BaseModel):
    id: UUID
    email: str
    target_role: Optional[str] = None
    summary: Optional[str] = None

    class Config:
        from_attributes = True


# Task/Pipeline Schemas
class PipelineResponse(BaseModel):
    status: str = Field(..., example="queued")
    task_id: UUID
    detail: str = Field(..., example="File accepted. Background processing started.")


class HealthResponse(BaseModel):
    status: str
    engine: str
    timestamp: float
