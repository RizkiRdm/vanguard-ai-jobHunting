import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.browser import BrowserManager
from core.mcp.mcp_browser import MCPBrowser

@pytest.mark.asyncio
async def test_browser_context_management():
    """Test browser lifecycle with mocked MCP to be instant."""
    mock_mcp = AsyncMock(spec=MCPBrowser)
    with patch("core.mcp.mcp_browser.MCPBrowser", return_value=mock_mcp):
        manager = BrowserManager()

        await manager.connect()
        # ... rest ...
        await manager.open_url("https://example.com")
        await manager.disconnect()
        
        mock_mcp.connect.assert_awaited_once()
        mock_mcp.disconnect.assert_awaited_once()
