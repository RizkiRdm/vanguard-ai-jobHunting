import pytest
from modules.agent.models import AgentTask, TaskStatus
from modules.generator.models import ScrapedJob
from core.orchestrator import JobOrchestrator
import uuid


@pytest.mark.asyncio
async def test_scraping_flow_no_api_hit():
    """
    Test E2E Scraping: Memastikan data diproses dan masuk DB menggunakan Mock.
    """
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    # 1. Inisialisasi Orchestrator
    orchestrator = JobOrchestrator()

    # 2. Eksekusi task (Ini akan memanggil Mock Gemini & Mock Browser)
    # Task type DISCOVERY akan memicu JobScraper.scrape_llm
    result = await orchestrator.execute_from_worker(
        task_id=task_id, user_id=user_id, task_type="DISCOVERY"
    )

    # 3. Verifikasi Return Value (Harus sesuai Fake JSON di Mock)
    assert result["job_title"] == "AI Architect"
    assert result["company_name"] == "Mock Corp"

    # 4. Verifikasi Database (Apakah ScrapedJob beneran ke-create?)
    db_job = await ScrapedJob.get(user_id=user_id)
    assert db_job.job_title == "AI Architect"
    assert str(db_job.user_id) == user_id

    print("✅ Scraping E2E (Mocked) Success: No API Token used!")
