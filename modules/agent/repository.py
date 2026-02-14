from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_
from uuid import UUID
from typing import List, Optional, Dict
from core.models_tech import AgentTask, AgentExecutionLog, LLMUsageLog


class AgentRepository:
    """
    Handles database operations for Agent Tasks, execution logs, and LLM usage auditing.
    Ensures data persistence and retrieval for the autonomous agent module.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_task(self, user_id: UUID, target_url: str) -> AgentTask:
        """Creates a new agent task record with an initial 'QUEUED' status."""
        task = AgentTask(user_id=user_id, target_url=target_url, status="QUEUED")
        self.db.add(task)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def get_task_by_id(self, task_id: UUID) -> Optional[AgentTask]:
        """
        Retrieves a specific task record by its unique identifier.
        """
        result = await self.db.execute(select(AgentTask).where(AgentTask.id == task_id))
        return result.scalars().first()

    async def get_failed_or_interrupted_tasks(self, user_id: UUID) -> List[AgentTask]:
        """
        Retrieves tasks that are in FAILED or STOPPED status for recovery.
        """
        result = await self.db.execute(
            select(AgentTask)
            .where(AgentTask.user_id == user_id)
            .where(or_(AgentTask.status == "FAILED", AgentTask.status == "STOPPED"))
            .order_by(desc(AgentTask.created_at))
        )
        return result.scalars().all()

    async def get_recent_logs(
        self, task_id: UUID, limit: int = 50
    ) -> List[AgentExecutionLog]:
        """
        Retrieves the most recent execution logs for a specific task, ordered by timestamp.
        """
        result = await self.db.execute(
            select(AgentExecutionLog)
            .where(AgentExecutionLog.task_id == task_id)
            .order_by(desc(AgentExecutionLog.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_task_cost_summary(self, task_id: UUID) -> Dict:
        """
        Calculates the total token usage and estimated cost for a specific task
        based on aggregated data from llm_usage_logs.
        """
        result = await self.db.execute(
            select(
                func.sum(LLMUsageLog.prompt_tokens).label("total_prompt"),
                func.sum(LLMUsageLog.completion_tokens).label("total_completion"),
                func.sum(LLMUsageLog.estimated_cost).label("total_cost"),
            ).where(LLMUsageLog.task_id == task_id)
        )
        row = result.first()
        return {
            "prompt_tokens": row.total_prompt or 0,
            "completion_tokens": row.total_completion or 0,
            "estimated_cost": row.total_cost or 0.0,
        }

    async def log_llm_usage(self, usage_data: LLMUsageLog):
        """
        Persists LLM usage metadata to the database for cost auditing purposes.
        """
        self.db.add(usage_data)
        await self.db.commit()
