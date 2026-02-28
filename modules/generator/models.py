from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class ScrapedJob(models.Model):
    id = fields.UUIDField(primary_key=True)
    user_id = fields.UUIDField(db_index=True)  # FK ke Users

    # Core Extraction Fields (Matching Gemini Output)
    job_title = fields.CharField(max_length=100)
    company_name = fields.CharField(max_length=150)
    location = fields.CharField(max_length=255, null=True)
    employment_type = fields.CharField(max_length=100, null=True)
    salary_range = fields.CharField(max_length=100, null=True)

    # Detailed Content
    job_description = fields.TextField()
    requirements = fields.JSONField(null=True)  # List of requirements

    # Metadata & Tracking
    source_url = fields.TextField()
    posted_date = fields.CharField(max_length=100, null=True)
    raw_html = fields.TextField(null=True)  # Untuk audit agent

    # Scoring for Ranking
    similarity_score = fields.FloatField(default=0.0)  # Hasil ranking relevansi

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "scraped_jobs"


# Generate Pydantic for API response
ScrapedJob_Pydantic = pydantic_model_creator(ScrapedJob, name="ScrapedJob")


class TailoredDocument(models.Model):
    id = fields.UUIDField(primary_key=True)
<<<<<<< HEAD
    user_id = fields.UUIDField(db_index=True)  # FK ke Users
=======
>>>>>>> 8a68e69 (refactor(core): improve scraping reliability and mock stability)
    task_id = fields.UUIDField(db_index=True)  # Relasi ke AgentTask
    doc_type = fields.CharField(max_length=50)  # 'CV' atau 'COVER_LETTER'
    content = fields.TextField()  # Hasil generate dari LLM
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "tailored_documents"


TailoredDocument_pydantic = pydantic_model_creator(
    TailoredDocument, name="TailoredDocument"
)
