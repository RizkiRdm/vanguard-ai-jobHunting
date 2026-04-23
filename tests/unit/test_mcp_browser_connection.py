import pytest
from core.mcp.mcp_browser import MCPBrowser

@pytest.mark.asyncio
async def test_mcp_browser_connect_init():
    browser = MCPBrowser()
    await browser.connect()
    assert browser.session is not None
    await browser.disconnect()
