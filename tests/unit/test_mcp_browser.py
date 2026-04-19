import pytest
from core.mcp.mcp_browser import MCPBrowser

@pytest.mark.asyncio
async def test_mcp_browser_init():
    browser = MCPBrowser()
    assert browser.server_params.command == "npx"
