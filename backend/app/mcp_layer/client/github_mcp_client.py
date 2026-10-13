"""MCP CLIENT side: speaks the MCP protocol to the GitHub MCP server.
Knows nothing about FastAPI, the LLM or business rules. Only: start, stop, list tools, call a tool."""
import json
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp.shared.exceptions import McpError

from app.core.exceptions import AppError, NotFoundError, UpstreamError
from app.mcp_layer.server.github_server_config import build_github_server_params
from app.models.tool_model import ToolSpec


class GitHubMCPClient:
    def __init__(self) -> None:
        self._stack = AsyncExitStack()
        self._session: ClientSession | None = None

    async def start(self) -> None:
        read, write = await self._stack.enter_async_context(stdio_client(build_github_server_params()))
        self._session = await self._stack.enter_async_context(ClientSession(read, write))
        await self._session.initialize()

    async def stop(self) -> None:
        await self._stack.aclose()

    async def list_tools(self) -> list[ToolSpec]:
        result = await self._session.list_tools()
        return [ToolSpec(t.name, t.description or "", t.inputSchema) for t in result.tools]

    async def call_tool(self, name: str, arguments: dict) -> str:
        try:
            result = await self._session.call_tool(name, arguments)
        except McpError as exc:
            raise self._translate(exc.error.message) from exc
        parts = []
        for item in result.content:
            text = getattr(item, "text", None) or getattr(getattr(item, "resource", None), "text", None)
            if text:
                parts.append(text)
        output = "\n".join(parts)
        if result.isError:
            raise self._translate(output or f"MCP tool '{name}' failed")
        return output

    @staticmethod
    def _translate(message: str) -> AppError:
        """Map MCP/GitHub failures onto our domain errors (404 vs 502)."""
        lowered = message.lower()
        if "not found" in lowered or "404" in lowered:
            return NotFoundError(message)
        return UpstreamError(message)

    async def call_tool_json(self, name: str, arguments: dict):
        text = await self.call_tool(name, arguments)
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
