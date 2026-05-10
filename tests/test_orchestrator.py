import pytest
import uuid
from unittest.mock import AsyncMock, patch
from core.orchestrator import JobOrchestrator
from modules.agent.models import TaskStatus

@pytest.mark.asyncio
async def test_orchestrator_discovery_spawns_tasks():
    with patch("core.scraper.JobScraper.scrape_llm", new_callable=AsyncMock) as mock_scrape:
        with patch("core.orchestrator.create_sub_task", new_callable=AsyncMock) as mock_create:
            with patch("core.orchestrator.update_task_status", new_callable=AsyncMock) as mock_status:
                
                # Setup mock scraper data
                mock_scrape.return_value = [{"source_url": "http://test.com", "job_title": "Dev", "company_name": "Acme"}]
                
                orchestrator = JobOrchestrator()
                # Mock browser to prevent actual browser launch
                orchestrator.browser.connect = AsyncMock()
                orchestrator.browser.open_url = AsyncMock()
                orchestrator.browser.disconnect = AsyncMock()
                
                valid_task_id = str(uuid.uuid4())
                valid_user_id = str(uuid.uuid4())
                
                result = await orchestrator._handle_discovery(valid_task_id, valid_user_id, {"base_url": "http://test.com"})
                
                assert result["spawned_tasks"] == 1
                assert mock_create.called
                mock_status.assert_called_once_with(valid_task_id, TaskStatus.COMPLETED)
