from tortoise import fields, models
from enum import Enum


class TaskStatus(str, Enum):
    DISCOVERY = "DISCOVERY"
<<<<<<< HEAD
    AUTOMATED_APPLY = "AUTOMATED_APPLY"
=======
>>>>>>> 8a68e69 (refactor(core): improve scraping reliability and mock stability)
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    AWAITING_USER = "AWAIT_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentTask(models.Model):
    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField(
        "models.User", related_name="tasks", on_delete=fields.SET_NULL, null=True
    )
    task_type = fields.CharField(max_length=20)
    metadata = fields.JSONField(default={})
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.QUEUED)
    subjective_question = fields.TextField(null=True)
    error_log = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    parent_id = fields.UUIDField(null=True, db_index=True)
    session_data_path = fields.CharField(max_length=255, null=True)
    last_url = fields.TextField(null=True)
    last_screenshot_path = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "agent_tasks"


class LLMUsageLog(models.Model):
    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="llm_logs", null=True)
    prompt_tokens = fields.IntField()
    completion_tokens = fields.IntField()
    total_tokens = fields.IntField()
    model_name = fields.CharField(max_length=50)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "llm_usage_logs"
