from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional
from core.security import mask_email


class UserProfileResponse(BaseModel):
    id: str
    email: str
    target_role: Optional[str] = None
    summary: Optional[str] = None

    @field_validator("email", mode="after")
    @classmethod
    def apply_masking(cls, v: str) -> str:
        # Using the mask_email function from core/security.py
        return mask_email(v)

    model_config = ConfigDict(from_attributes=True)
