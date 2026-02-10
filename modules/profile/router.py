from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from core.database import get_db
from modules.profile.repository import ProfileRepository
from modules.profile.service import ProfileService

# Setup Templates for this module
# Note: Jinja2 will look into the 'templates' folder at the root
templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/profile", tags=["Profile"])

# TODO: update when enter to stagging branch
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"


@router.get("/", response_class=HTMLResponse)
async def get_profile_page(request: Request, db: AsyncSession = Depends(get_db)):
    repo = ProfileRepository(db)
    profile = await repo.get_profile_by_user_id(UUID(MOCK_USER_ID))

    context = {"request": request, "profile": profile}
    return templates.TemplateResponse("pages/profile.html", context)


# Endpoint khusus HTMX untuk Inline Edit Pengalaman Kerja
@router.get("/experience/{exp_id}/edit", response_class=HTMLResponse)
async def edit_experience_form(
    request: Request, exp_id: UUID, db: AsyncSession = Depends(get_db)
):
    # Logic: Ambil data lama, balikin form
    # Untuk simplifikasi Sprint 3, kita fokus ke view profile dulu
    return HTMLResponse("Form Edit Disini (Soon)")


@router.post("/parse", response_class=HTMLResponse)
async def parse_cv(
    request: Request, cv_text: str = Form(...), db: AsyncSession = Depends(get_db)
):
    repo = ProfileRepository(db)
    service = ProfileService(repo)

    await service.parse_cv_with_ai(UUID(MOCK_USER_ID), cv_text)

    # Setelah parse, suruh HTMX refresh bagian profil
    profile = await repo.get_profile_by_user_id(UUID(MOCK_USER_ID))
    return templates.TemplateResponse(
        "pages/profile_content.html", {"request": request, "profile": profile}
    )
