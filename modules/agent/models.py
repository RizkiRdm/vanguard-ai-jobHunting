from enum import Enum
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


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


class AgentTask(models.Model):
    """Main orchestrator table to track AI agent activities."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True)  # Linked to Auth User

    task_type = fields.CharEnumField(TaskType)
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.QUEUED)

    # Flexible storage for AI state, target URLs, and answers
    metadata = fields.JSONField(default={})

    # Human-in-the-loop field
    subjective_question = fields.TextField(null=True)

    # Execution tracing
    last_url = fields.TextField(null=True)
    last_screenshot_path = fields.CharField(max_length=255, null=True)
    session_data_path = fields.CharField(max_length=255, null=True)
    error_log = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    # Self-reference for sub-tasks if needed
    parent_id = fields.UUIDField(null=True, db_index=True)

    class Meta:
        table = "agent_tasks"


class LLMUsageLog(models.Model):
    """Tracks token usage and AI costs per user."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True, null=True)

    model_name = fields.CharField(max_length=100)
    prompt_tokens = fields.IntField(default=0)
    completion_tokens = fields.IntField(default=0)
    total_tokens = fields.IntField(default=0)

    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "llm_usage_logs"


# Pydantic creators for FastAPI serialization
AgentTask_Pydantic = pydantic_model_creator(AgentTask, name="AgentTask")
