from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# Setup Templates for this module
# Note: Jinja2 will look into the 'templates' folder at the root
templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("/", response_class=HTMLResponse)
async def get_profile_page(request: Request):
    """
    Renders the User Profile management page.

    ENGINEERING NOTE:
    To include navbar and sidebar, we don't import them here in Python.
    Instead, in 'templates/pages/profile.html', we use:
    {% extends 'base.html' %}

    The 'base.html' already contains:
    {% include 'components/navbar.html' %}
    {% include 'components/sidebar.html' %}
    """
    context = {"request": request}

    # HTMX Logic: If the request comes from HTMX, return only the partial fragment
    # to save bandwidth and improve performance on low-spec hardware (Celeron life!)
    if request.headers.get("HX-Request"):
        return templates.TemplateResponse("pages/profile.html", context)

    # Default: Return the full page which extends base.html
    return templates.TemplateResponse("pages/profile.html", context)
