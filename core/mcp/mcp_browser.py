import asyncio
import os
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from core.custom_logging import logger

class MCPBrowser:
    def __init__(self):
        # Use absolute path to the locally installed package
        node_modules_path = os.path.abspath("node_modules/@playwright/mcp/index.js")
        self.server_params = StdioServerParameters(
            command="node",
            args=[node_modules_path, "--headless"],
            env=None
        )
        self.session = None
        self.exit_stack = None

    async def connect(self):
        self.exit_stack = AsyncExitStack()
        read, write = await self.exit_stack.enter_async_context(stdio_client(self.server_params))
        self.session = ClientSession(read, write)
        await self.session.initialize()
        logger.info("mcp_session_initialized")
        if not self.session:
            logger.error("mcp_session_null_after_init")

    async def disconnect(self):
        if self.exit_stack:
            await self.exit_stack.aclose()

    async def open_url(self, url: str):
        if not self.session:
            raise RuntimeError("MCP Session not initialized. Call connect() first.")
        return await self.session.call_tool("playwright_goto", {"url": url})

    async def screenshot(self, name: str):
        if not self.session:
            raise RuntimeError("MCP Session not initialized. Call connect() first.")
        return await self.session.call_tool("playwright_screenshot", {"name": name})
