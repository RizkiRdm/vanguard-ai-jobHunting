from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from core.browser_engine import browser_engine
from core.models_tech import AgentTask, AgentExecutionLog
from modules.agent.tools import AgentTools
from modules.agent.planner import AgentPlanner
from shared.schemas import Task


class AgentService:
    """
    Orchestrates the agent execution, database updates, and logging.
    Connects the Planner with the actual system resources and DB.
    """

    def __init__(self, db: AsyncSession, api_key: str):
        self.db = db
        self.api_key = api_key

    async def create_log(
        self, task_id: UUID, message: str, level: str = "INFO", screenshot: str = None
    ):
        """Creates a real-time log entry in the database for HTMX polling."""
        log = AgentExecutionLog(
            task_id=task_id, message=message, level=level, screenshot_path=screenshot
        )
        self.db.add(log)
        await self.db.commit()

    async def update_task_status(self, task_id: UUID, status: str, error: str = None):
        """Updates the agent_tasks table status."""
        stmt = (
            update(AgentTask)
            .where(AgentTask.id == task_id)
            .values(
                status=status,
                error_message=error,
                end_time=(
                    datetime.now()
                    if status in ["COMPLETED", "FAILED", "STOPPED"]
                    else None
                ),
                start_time=(
                    datetime.now() if status == "RUNNING" else AgentTask.start_time
                ),
            )
        )
        await self.db.execute(stmt)
        await self.db.commit()

    async def run_autonomous_task(self, task_id: UUID, objective: str):
        """
        The main lifecycle of an autonomous agent run.
        1. Initialize Browser
        2. Set up Tools & Planner
        3. Execute Loop
        4. Cleanup
        """
        page = None
        try:
            # 1. Update Status to Running
            await self.update_task_status(task_id, "RUNNING")
            await self.create_log(
                task_id, f"Initializing browser for task: {objective}"
            )

            # 2. Start Browser Engine & Page
            await browser_engine.start(
                headless=True
            )  # Set to False for local debugging
            page = await browser_engine.get_page()

            # 3. Initialize Tools and Planner
            tools = AgentTools(page)
            planner = AgentPlanner(tools, self.api_key)

            await self.create_log(task_id, "Agent is now thinking and observing...")

            # 4. Execute the Reasoning Loop (Planner)
            # Note: We wrap this in a way that we could potentially capture
            # intermediate thoughts for logging
            await planner.execute_task(objective)

            # 5. Mark as Completed
            await self.update_task_status(task_id, "COMPLETED")
            await self.create_log(
                task_id, "Objective achieved. Task finalized.", level="INFO"
            )

        except Exception as e:
            # Handle failures
            error_msg = str(e)
            await self.update_task_status(task_id, "FAILED", error=error_msg)
            await self.create_log(
                task_id, f"Critical Error: {error_msg}", level="ERROR"
            )
            print(f"Agent Task {task_id} Failed: {error_msg}")

        finally:
            # 6. Safety Cleanup
            if page:
                await page.close()
            # We don't close the browser_engine entirely to allow pool reuse
            # unless it's the last task.
