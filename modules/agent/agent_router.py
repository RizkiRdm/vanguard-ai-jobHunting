from fastapi import APIRouter, Depends, Response
from core.security import get_current_user_from_cookie, create_access_token

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/login-test")
async def login_test(response: Response):
    """Sesuai Contract: JWT disimpan dalam httpOnly cookie"""
    token = create_access_token(data={"sub": "test_user_id"})
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,  # Set True di production dengan HTTPS
        samesite="lax",
    )
    return {"message": "Login successful"}


@router.post("/scrape")
async def scrape_web(user_id: str = Depends(get_current_user_from_cookie)):
    """Endpoint sensitif yang dilindungi JWT & Rate Limit"""
    return {"message": f"Scraping started for user {user_id}"}
