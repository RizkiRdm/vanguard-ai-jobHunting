from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class ScrapedJob(models.Model):
    """Stores job listings found by the AI during the Discovery phase."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True)

    # Core Fields
    job_title = fields.CharField(max_length=200)
    company_name = fields.CharField(max_length=200)
    location = fields.CharField(max_length=255, null=True)
    employment_type = fields.CharField(max_length=100, null=True)
    salary_range = fields.CharField(max_length=100, null=True)

    # Content & Source
    job_description = fields.TextField()
    requirements = fields.JSONField(null=True)
    source_url = fields.TextField()

    # Metadata for Agent Tracking
    similarity_score = fields.FloatField(default=0.0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "scraped_jobs"


class TailoredDocument(models.Model):
    """Stores AI-generated CVs or Cover Letters tailored to specific tasks."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True)
    task_id = fields.UUIDField(db_index=True)

    doc_type = fields.CharField(max_length=50)  # 'CV' or 'COVER_LETTER'
    content = fields.TextField()

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tailored_documents"


class LLMUsageLog(models.Model):
    """Audits AI token consumption per user and model."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True, null=True)

    model_name = fields.CharField(max_length=100)
    prompt_tokens = fields.IntField()
    completion_tokens = fields.IntField()
    total_tokens = fields.IntField()

    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "llm_usage_logs"


# Pydantic models for API serialization
ScrapedJob_Pydantic = pydantic_model_creator(ScrapedJob, name="ScrapedJob")
TailoredDocument_Pydantic = pydantic_model_creator(
    TailoredDocument, name="TailoredDocument"
)
