import os
from uuid import UUID
from fastapi import APIRouter, Depends, BackgroundTasks, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from modules.agent.repository import AgentRepository
from modules.agent.service import AgentService

# Initialize templates
templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix="/agent", tags=["Agent Automation"])

# Mocking user ID for current development stage (Replace with actual auth later)
MOCK_USER_ID = "00000000-0000-0000-0000-000000000001"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


@router.get("/", response_class=HTMLResponse)
async def get_agent_console(request: Request):
    """
    Renders the Agent Control Center page.
    """
    context = {"request": request}
    return templates.TemplateResponse("pages/agent.html", context)


@router.post("/task/start", response_class=HTMLResponse)
async def start_agent_task(
    background_tasks: BackgroundTasks,
    target_url: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Triggers the autonomous agent execution in the background using FastAPI BackgroundTasks.
    """
    repo = AgentRepository(db)
    service = AgentService(db, GEMINI_API_KEY)

    # 1. Create task entry in DB (Status: QUEUED)
    task = await repo.create_task(UUID(MOCK_USER_ID), target_url)

    # 2. Add the autonomous run to background tasks
    background_tasks.add_task(
        service.run_autonomous_task,
        task_id=task.id,
        objective=f"Analyze {target_url} for job opportunities and navigate accordingly.",
    )

    # 3. Return an HTMX fragment to initialize the monitoring UI and start polling
    return f"""
    <div id="agent-monitor" class="bg-slate-900 border border-slate-800 rounded-2xl p-6 mt-6 shadow-2xl">
        <div class="flex items-center justify-between mb-4">
            <div class="flex items-center space-x-3">
                <div class="w-3 h-3 bg-emerald-500 rounded-full animate-ping"></div>
                <h3 class="text-white font-bold">Live Agent Activity</h3>
            </div>
            <span id="task-status-{task.id}" class="px-3 py-1 bg-blue-500/20 text-blue-400 text-xs font-mono rounded-full border border-blue-500/30">
                RUNNING
            </span>
        </div>
        
        <div id="log-container-{task.id}" 
             class="space-y-2 h-80 overflow-y-auto font-mono text-xs text-slate-400 bg-slate-950/50 p-4 rounded-xl border border-slate-800/50"
             hx-get="/agent/task/{task.id}/logs" 
             hx-trigger="every 2s"
             hx-swap="innerHTML">
            <p class="text-blue-400 italic">>> Initializing browser engine...</p>
            <p class="text-slate-500">>> Requesting task ID: {task.id}</p>
        </div>
    </div>
    """


@router.get("/task/{task_id}/logs", response_class=HTMLResponse)
async def get_task_logs(
    request: Request, task_id: UUID, db: AsyncSession = Depends(get_db)
):
    """
    Endpoint for HTMX polling to fetch the latest agent logs.
    """
    repo = AgentRepository(db)
    logs = await repo.get_recent_logs(task_id)
    task = await repo.get_task_by_id(task_id)

    # Normally we'd use a template fragment here, but for brevity in the response:
    log_html = ""
    for log in reversed(logs):  # Show oldest to newest in the UI
        color = "text-red-400" if log.level == "ERROR" else "text-slate-300"
        log_html += f'<div class="py-1 border-b border-slate-800/30 {color}"><span class="text-slate-600">[{log.timestamp.strftime("%H:%M:%S")}]</span> {log.message}</div>'

    # If the task is finished, we can include a special swap to stop polling
    if task and task.status in ["COMPLETED", "FAILED"]:
        status_color = (
            "bg-emerald-500/20 text-emerald-400"
            if task.status == "COMPLETED"
            else "bg-red-500/20 text-red-400"
        )
        log_html += f"""
        <div hx-swap-oob="outerHTML:#task-status-{task.id}">
            <span id="task-status-{task.id}" class="px-3 py-1 {status_color} text-xs font-mono rounded-full border border-current">
                {task.status}
            </span>
        </div>
        <script>console.log("Task Finished - Polling should stop if hx-trigger is removed");</script>
        """
        # To stop polling, we could wrap the response in a div without hx-get
        return f'<div hx-get="false" hx-trigger="none">{log_html}</div>'

    return (
        log_html
        if log_html
        else '<p class="text-slate-600 italic">Waiting for logs...</p>'
    )
