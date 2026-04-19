import pytest
from core.mcp.mcp_browser import MCPBrowser

@pytest.mark.asyncio
async def test_mcp_flow():
    browser = MCPBrowser()
    try:
        await browser.connect()
        await browser.open_url("https://google.com")
        await browser.screenshot("test.png")
    finally:
        await browser.disconnect()
