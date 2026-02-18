import pytest
import os
import json
from unittest.mock import AsyncMock, patch
from core.ai_agent import VanguardAI
from PIL import Image


@pytest.fixture(autouse=True)
def setup_env():
    """Mock environment variable for all tests."""
    with patch.dict(os.environ, {"GEMINI_API_KEY": "test_key_123"}):
        yield


@pytest.mark.asyncio
async def test_analyze_screen_success(tmp_path):
    # Create a dummy image file
    test_img = tmp_path / "browser_state.png"
    Image.new("RGB", (1280, 720), color="white").save(test_img)

    agent = VanguardAI()

    # Mocking Gemini response with extra text to test regex robustness
    mock_response = AsyncMock()
    mock_response.text = 'Here is the result: {"action": "click", "selector": "#apply-btn", "value": "", "reasoning": "Found the button."} end of message.'

    with patch("core.ai_agent.VanguardAI._call_gemini_api", return_value=mock_response):
        decision = await agent.analyze_screen(str(test_img), "Apply for the job")

        assert decision["action"] == "click"
        assert decision["selector"] == "#apply-btn"
        assert "reasoning" in decision


@pytest.mark.asyncio
async def test_analyze_screen_missing_file():
    agent = VanguardAI()
    with pytest.raises(FileNotFoundError):
        await agent.analyze_screen("invalid/path/screenshot.png", "Goal")


@pytest.mark.asyncio
async def test_analyze_screen_invalid_json_fallback(tmp_path):
    test_img = tmp_path / "error_state.png"
    Image.new("RGB", (100, 100)).save(test_img)

    agent = VanguardAI()

    mock_response = AsyncMock()
    mock_response.text = "I am sorry, I cannot see anything."  # String tanpa JSON

    with patch("core.ai_agent.VanguardAI._call_gemini_api", return_value=mock_response):
        decision = await agent.analyze_screen(str(test_img), "Goal")

        assert decision["action"] == "fail"
        # FIX: Sesuaikan dengan string yang dilempar di core/ai_agent.py
        assert "No JSON object found" in decision["reasoning"]


@pytest.mark.asyncio
async def test_ai_agent_api_retry_exhaustion(tmp_path):
    test_img = tmp_path / "retry_test.png"
    Image.new("RGB", (1, 1)).save(test_img)

    agent = VanguardAI()

    with patch(
        "core.ai_agent.VanguardAI._call_gemini_api",
        side_effect=Exception("API Connection Refused"),
    ):
        decision = await agent.analyze_screen(str(test_img), "Goal")

        assert decision["action"] == "fail"
        assert "Critical error" in decision["reasoning"]
