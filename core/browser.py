import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from core.mcp.mcp_browser import MCPBrowser
from core.custom_logging import logger

class BrowserManager:
    def __init__(self):
        self.log = logger.bind(service="browser_manager")
        self.mcp = MCPBrowser()
        self.screenshot_dir = Path("storage/screenshots")
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

    async def connect(self):
        await self.mcp.connect()

    async def disconnect(self):
        await self.mcp.disconnect()

    async def open_url(self, url: str):
        return await self.mcp.open_url(url)

    async def take_screenshot(self, name: str) -> str:
        res = await self.mcp.screenshot(name)
        # Assume MCP returns path or we handle it
        return res if isinstance(res, str) else str(self.screenshot_dir / f"{name}.png")

    async def perform_action(self, action: str, params: Dict[str, Any]):
        return await self.mcp.session.call_tool(action, params)
