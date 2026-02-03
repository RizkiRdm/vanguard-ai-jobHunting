import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from core.database import Base


class TimestampMixin:
    """Mixin to add created_at and updated_at to all models"""

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )


class AgentTask(Base, TimestampMixin):
    """
    Stores metadata for each autonomous agent execution.
    Referenced in DB_SCHEMA.md
    """

    __tablename__ = "agent_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), index=True, nullable=False
    )  # Simplified for Foundation stage

    status = Column(
        String(20), default="QUEUED", nullable=False
    )  # QUEUED, RUNNING, etc.
    target_url = Column(String(512), nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)


class AgentExecutionLog(Base):
    """
    Real-time logs for HTMX activity streaming.
    No updated_at needed for logs.
    """

    __tablename__ = "agent_execution_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_tasks.id", ondelete="CASCADE"),
        nullable=False,
    )

    level = Column(String(10), default="INFO")  # INFO, WARNING, ERROR
    message = Column(Text, nullable=False)
    screenshot_path = Column(String(512), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class LLMUsageLog(Base):
    """
    Cost auditing and token usage tracking.
    """

    __tablename__ = "llm_usage_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_tasks.id", ondelete="SET NULL"),
        nullable=True,
    )

    model_name = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
