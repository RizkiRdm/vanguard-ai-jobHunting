import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPBrowser:
    def __init__(self):
        self.server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@playwright/mcp@latest"],
            env=None
        )
        self.session = None
        self.exit_stack = None

    async def connect(self):
        self.exit_stack = AsyncExitStack()
        read, write = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()

    async def disconnect(self):
        if self.exit_stack:
            await self.exit_stack.aclose()

    async def open_url(self, url: str):
        return await self.session.call_tool("playwright_goto", {"url": url})

    async def screenshot(self, name: str):
        return await self.session.call_tool("playwright_screenshot", {"name": name})
