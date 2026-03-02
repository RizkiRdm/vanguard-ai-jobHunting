from tortoise import fields, models
from enum import Enum


class TaskStatus(str, Enum):
    DISCOVERY = "DISCOVERY"
    APPLYING = "APPLYING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    AWAITING_USER = "AWAITING_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentTask(models.Model):
    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField(
        "models.User", related_name="tasks", on_delete=fields.SET_NULL, null=True
    )
    task_type = fields.CharField(max_length=20)
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.QUEUED)
    subjective_question = fields.TextField(null=True)
    error_log = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "agent_tasks"


class LLMUsageLog(models.Model):
    id = fields.UUIDField(primary_key=True)
    # Ini boleh tetap CharField atau FK, terserah pilihan lo
    user = fields.ForeignKeyField("models.User", related_name="llm_logs", null=True)
    prompt_tokens = fields.IntField()
    completion_tokens = fields.IntField()
    total_tokens = fields.IntField()
    model_name = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "llm_usage_logs"
