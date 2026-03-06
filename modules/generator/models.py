from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class ScrapedJob(models.Model):
    """Stores job listings with detailed extraction for AI matching."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True)

    job_title = fields.CharField(max_length=200)
    company_name = fields.CharField(max_length=200)
    location = fields.CharField(max_length=255, null=True)
    job_description = fields.TextField()

    # Metadata for ranking
    similarity_score = fields.FloatField(default=0.0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "scraped_jobs"


class TailoredDocument(models.Model):
    """Stores career documents with versioning."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True)
    task_id = fields.UUIDField(db_index=True)

    doc_type = fields.CharField(max_length=50)  # CV or COVER_LETTER
    content = fields.TextField()

    # New: Track token cost for this specific document
    token_cost = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tailored_documents"


class LLMUsageLog(models.Model):
    """Centralized audit log for AI expenses."""

    id = fields.UUIDField(pk=True)
    user_id = fields.UUIDField(db_index=True, null=True)
    model_name = fields.CharField(max_length=100)
    total_tokens = fields.IntField()
    timestamp = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "llm_usage_logs"


ScrapedJob_Pydantic = pydantic_model_creator(ScrapedJob, name="ScrapedJob")
