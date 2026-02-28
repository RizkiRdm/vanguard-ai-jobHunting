from modules.generator.models import TailoredDocument
from core.ai_agent import VanguardAI


async def generate_tailored_document(
    user_id: str, task_id: str, job_context: str, doc_type: str = "CV"
):
    """
    Menggunakan Gemini untuk membuat CV atau Cover Letter yang disesuaikan dengan job description.
    """
    ai = VanguardAI()

    prompt = f"""
You are a professional career assistant.

Task:
Create a tailored {doc_type} specifically optimized for the job described below.

Job Description:
{job_context}

Requirements:
- Use a professional and confident tone.
- Align skills and experiences directly with the job requirements.
- Highlight measurable achievements where possible.
- Avoid generic statements.
- Optimize for ATS (use relevant keywords from the job description naturally).
- Keep it concise and impactful.
- Do not fabricate experience that is not implied by the provided context.

Output only the final {doc_type} content.
Do not include explanations.
"""

    # Generate content via LLM
    response = await ai.client.models.generate_content(
        model=ai.model_id, contents=prompt
    )
    tailored_content = response.text

    # Simpan ke DB
    doc = await TailoredDocument.create(
        task_id=task_id, doc_type=doc_type, content=tailored_content
    )

    return doc
