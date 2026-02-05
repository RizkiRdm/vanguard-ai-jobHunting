from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/agent", tags=["Agent Automation"])


@router.get("/")
async def get_agent_console(request: Request):
    """
    Renders the Agent Control Center page.
    """
    context = {"request": request}
    return templates.TemplateResponse("pages/agent.html", context)


@router.post("/task/start")
async def start_agent_task(request: Request):
    """
    Endpoint to trigger a new job hunting task.
    """
    # For now, return a placeholder status toast
    return "<div>Agent Started! (Mock)</div>"
