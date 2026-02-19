from tortoise import fields, models, transactions
from enum import Enum


class TaskStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    AWAITING_USER = "AWAITING_USER"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentTask(models.Model):
    id = fields.UUIDField(primary_key=True)
    user = fields.ForeignKeyField("models.User", related_name="tasks")
    task_type = fields.CharField(max_length=20)  # DISCOVERY, TAILORING, APPLYING
    status = fields.CharEnumField(TaskStatus, default=TaskStatus.QUEUED)
    subjective_question = fields.TextField(null=True)
    error_log = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "agent_tasks"
