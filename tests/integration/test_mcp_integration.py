import pytest
from core.mcp.mcp_browser import MCPBrowser

@pytest.mark.asyncio
async def test_mcp_integration():
    browser = MCPBrowser()
    try:
        await browser.connect()
        result = await browser.open_url("https://example.com")
        assert result is not None
    finally:
        await browser.disconnect()
