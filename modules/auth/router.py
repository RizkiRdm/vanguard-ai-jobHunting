from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from core.database import get_db
from modules.auth.service import AuthService
from core.security import create_token, ACCESS_TOKEN_EXPIRE_MINUTES

# Logger initialization
logger = logging.getLogger("AuthRouter")
templates = Jinja2Templates(directory="templates")

router = APIRouter(tags=["Authentication"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Renders the login page.
    Supports HTMX fragments for smooth transitions.
    """
    context = {"request": request, "title": "Login - Vanguard AI"}

    # Handle HTMX request for partial rendering
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("pages/login_fragment.html", context)

    return templates.TemplateResponse("pages/login_full.html", context)


@router.post("/login")
async def login_process(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Handles the user authentication process.
    Generates JWTs and stores them in secure HTTP-Only cookies.
    """
    logger.info(f"Attempting login for user: {username}")

    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(username, password)

    if user:
        logger.info(f"Login successful for user ID: {user.id}")

        # 1. Prepare token payload data
        token_data = {"sub": str(user.id), "email": user.email}

        # 2. Generate Access & Refresh Tokens using security utilities
        access_token = create_token(data=token_data)
        refresh_token = create_token(data=token_data, is_refresh=True)

        # 3. Create redirect response to dashboard
        response = RedirectResponse(
            url="/dashboard", status_code=status.HTTP_303_SEE_OTHER
        )

        # 4. Set Access Token in Cookie (Short-lived)
        response.set_cookie(
            key="vanguard_access_token",
            value=access_token,
            httponly=True,
            secure=True,  # Recommended for HTTPS
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        # 5. Set Refresh Token in Cookie (Long-lived)
        response.set_cookie(
            key="vanguard_refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/auth/refresh",  # Restrict sending refresh token to specific endpoint
            max_age=7 * 24 * 3600,  # 7 days
        )

        return response

    # If authentication fails
    logger.warning(f"Login failed for email: {username}")
    context = {
        "request": request,
        "error": "Invalid email or password.",
        "title": "Login - Vanguard AI",
    }

    # Use HTMX specific error component if requested
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("components/auth_error.html", context)

    return templates.TemplateResponse("pages/login_full.html", context)


@router.get("/logout")
async def logout():
    """
    Clears session cookies and redirects to the login page.
    """
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)

    # Remove both tokens from the client browser
    response.delete_cookie("vanguard_access_token")
    response.delete_cookie("vanguard_refresh_token")

    logger.info("User logged out and tokens cleared.")
    return response
