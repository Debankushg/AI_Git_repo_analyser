"""MCP SERVER side.

We do not implement an MCP server: GitHub's is an external program. This module only describes
how to LAUNCH it (as a child process speaking MCP over stdin/stdout). Default: the npm package
@modelcontextprotocol/server-github via npx. Change github_mcp_command / github_mcp_args in
.env to use GitHub's official Docker server instead.
"""
from mcp import StdioServerParameters

from app.core.config import settings


def build_github_server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=settings.github_mcp_command,
        args=settings.github_mcp_args,
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": settings.github_personal_access_token},
    )
