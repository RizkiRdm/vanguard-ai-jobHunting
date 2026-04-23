from enum import Enum
from sqlalchemy import String, Integer, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from uuid import UUID, uuid4
from datetime import datetime
from core.database import Base

class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    AWAIT_USER = "AWAIT_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class TaskType(str, Enum):
    DISCOVERY = "DISCOVERY"
    APPLYING = "APPLYING"

class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True)
    task_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default=TaskStatus.QUEUED.value)
    meta_data: Mapped[dict] = mapped_column(JSON, default={})
    subjective_question: Mapped[str] = mapped_column(Text, nullable=True)
    last_url: Mapped[str] = mapped_column(Text, nullable=True)
    last_screenshot_path: Mapped[str] = mapped_column(String(255), nullable=True)
    session_data_path: Mapped[str] = mapped_column(String(255), nullable=True)
    error_log: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    parent_id: Mapped[UUID] = mapped_column(nullable=True, index=True)

class AgentLLMUsageLog(Base):
    __tablename__ = "agent_llm_usage_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(index=True, nullable=True)
    model_name: Mapped[str] = mapped_column(String(100))
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    timestamp: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
