from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from uuid import UUID
from typing import List, Optional
from core.models_tech import AgentTask, AgentExecutionLog


class AgentRepository:
    """
    Handles database operations for Agent Tasks and their execution logs.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, user_id: UUID, target_url: str) -> AgentTask:
        """Creates a new agent task record in QUEUED status."""
        task = AgentTask(user_id=user_id, target_url=target_url, status="QUEUED")
        self.db.add(task)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task_by_id(self, task_id: UUID) -> Optional[AgentTask]:
        """Fetcles a specific task by its ID."""
        result = await self.db.execute(select(AgentTask).where(AgentTask.id == task_id))
        return result.scalars().first()

    async def get_recent_logs(
        self, task_id: UUID, limit: int = 50
    ) -> List[AgentExecutionLog]:
        """Fetches the latest execution logs for a specific task."""
        result = await self.db.execute(
            select(AgentExecutionLog)
            .where(AgentExecutionLog.task_id == task_id)
            .order_by(desc(AgentExecutionLog.timestamp))
            .limit(limit)
        )
        return result.scalars().all()
