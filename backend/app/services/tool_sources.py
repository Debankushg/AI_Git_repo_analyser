"""Where the AI's tools come from. GitHub repos use the GitHub MCP server (read + approval-gated write tools);
every other host gets a small read-only toolset backed by its provider."""
import json
from typing import Protocol

from app.models.repo_ref_model import RepoRef
from app.models.tool_model import ToolSpec
from app.providers.base_git_provider import BaseGitProvider
from app.repositories.github_repository import GitHubRepository


class ToolSource(Protocol):
    can_write: bool

    async def list_tools(self) -> list[ToolSpec]: ...
    async def call(self, name: str, args: dict) -> str: ...


class McpToolSource:
    can_write = True

    def __init__(self, github: GitHubRepository) -> None:
        self._github = github

    async def list_tools(self) -> list[ToolSpec]:
        return await self._github.list_tools()

    async def call(self, name: str, args: dict) -> str:
        return await self._github.call_tool(name, args)


class ProviderToolSource:
    can_write = False

    def __init__(self, provider: BaseGitProvider, ref: RepoRef) -> None:
        self._provider, self._ref = provider, ref

    async def list_tools(self) -> list[ToolSpec]:
        obj = lambda props, req=(): {"type": "object", "properties": props, "required": list(req)}
        tools = [
            ToolSpec("list_directory", "List files and folders at a path of the repository (empty path = root).", obj({"path": {"type": "string"}})),
            ToolSpec("read_file", "Read the text content of a file in the repository.", obj({"path": {"type": "string"}}, ["path"])),
            ToolSpec("list_commits", "List the most recent commits (message, author, date).", obj({"limit": {"type": "integer"}})),
        ]
        if self._provider.supports_pull_requests:
            tools.append(ToolSpec("list_pull_requests", "List open pull/merge requests.", obj({})))
        return tools

    async def call(self, name: str, args: dict) -> str:
        p, ref = self._provider, self._ref
        if name == "list_directory":
            return json.dumps([{"name": e.name, "path": e.path, "type": e.type} for e in await p.list_contents(ref, args.get("path", ""), None)])
        if name == "read_file":
            f = await p.read_file(ref, args["path"], None)
            return "[binary file]" if f.is_binary else f.content
        if name == "list_commits":
            commits = await p.list_commits(ref, min(int(args.get("limit", 20)), 50))
            return json.dumps([{"sha": c.sha[:8], "author": c.author_name, "date": c.date, "message": c.message.strip()[:300]} for c in commits])
        if name == "list_pull_requests":
            return json.dumps([{"number": r.number, "title": r.title, "draft": r.draft, "author": (r.user or {}).get("login"), "created_at": r.created_at} for r in await p.list_pull_requests(ref)])
        raise ValueError(f"Unknown tool {name}")
