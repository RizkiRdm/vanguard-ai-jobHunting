import uuid
from core.ai_agent import VanguardAI
from modules.generator.models import TailoredDocument
from core.custom_logging import logger

log = logger.bind(service="generator_service")


async def generate_tailored_document(
    user_id: str,
    task_id: str,
    job_context: str,
    profile_summary: str,
    doc_type: str = "CV",
) -> TailoredDocument:
    """
    Uses Gemini to create a highly optimized career document based on job context and user profile.
    """
    ai = VanguardAI()

    prompt = f"""
    Role: Professional Career Consultant
    Task: Create a tailored {doc_type} for the following job.
    
    [USER PROFILE SUMMARY]
    {profile_summary}
    
    [JOB DESCRIPTION]
    {job_context}
    
    Guidelines:
    - Use a professional, high-impact tone.
    - Match user skills directly with job requirements (ATS Optimization).
    - Highlight measurable achievements.
    - Output ONLY the {doc_type} content without any conversational text.
    """

    try:
        # Generate content using the new SDK syntax
        response = ai.client.models.generate_content(model=ai.model_id, contents=prompt)

        if not response.text:
            raise ValueError("AI returned empty content")

        # Create and persist the document
        doc = await TailoredDocument.create(
            id=uuid.uuid4(),
            user_id=uuid.UUID(user_id),
            task_id=uuid.UUID(task_id),
            doc_type=doc_type,
            content=response.text,
        )

        log.info("document_generated", doc_id=str(doc.id), type=doc_type)
        return doc

    except Exception as e:
        log.error("generation_failed", error=str(e))
        raise
