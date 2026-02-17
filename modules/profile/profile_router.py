from fastapi import APIRouter, HTTPException
from modules.profile.models import User, UserProfile
from shared.schemas import UserProfileResponse

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
