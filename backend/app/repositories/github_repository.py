"""Data-access layer for GitHub. Services call this; it calls the MCP client.
Returns raw GitHub JSON; mapping to API schemas is the service's job."""
import httpx

from app.core.config import settings
from app.core.exceptions import NotFoundError, UpstreamError
from app.mcp_layer.client.github_mcp_client import GitHubMCPClient
from app.models.tool_model import ToolSpec


class GitHubRepository:
    def __init__(self, mcp: GitHubMCPClient) -> None:
        self._mcp = mcp

    async def search_repositories(self, query: str, per_page: int = 50):
        return await self._mcp.call_tool_json("search_repositories", {"query": query, "perPage": per_page})

    async def get_contents(self, owner: str, repo: str, path: str = "", ref: str | None = None):
        args = {"owner": owner, "repo": repo, "path": path}
        if ref:
            args["branch"] = ref  # parameter name used by @modelcontextprotocol/server-github
        return await self._mcp.call_tool_json("get_file_contents", args)

    async def get_repository_info(self, owner: str, repo: str) -> dict:
        """Full repository metadata (language, stars, default branch...) from the GitHub REST API.
        The MCP server's search result only carries a reduced set of fields."""
        headers = {"Accept": "application/vnd.github+json", "Authorization": f"Bearer {settings.github_personal_access_token}"}
        async with httpx.AsyncClient(timeout=20) as http:
            res = await http.get(f"https://api.github.com/repos/{owner}/{repo}", headers=headers)
        if res.status_code == 404:
            raise NotFoundError(f"Repository {owner}/{repo} was not found, or your token can't access it.")
        if res.status_code in (401, 403):
            raise UpstreamError("GitHub rejected the token (invalid, expired or rate limited).")
        if res.status_code != 200:
            raise UpstreamError(f"GitHub returned {res.status_code} for {owner}/{repo}")
        return res.json()

    async def get_raw_file(self, owner: str, repo: str, path: str, ref: str | None = None) -> bytes:
        """Exact file bytes via the GitHub REST API. Used for binary files (images): the MCP server
        returns file contents as UTF-8 text, which corrupts binary data."""
        headers = {
            "Accept": "application/vnd.github.raw+json",
            "Authorization": f"Bearer {settings.github_personal_access_token}",
        }
        async with httpx.AsyncClient(follow_redirects=True, timeout=20) as http:
            res = await http.get(f"https://api.github.com/repos/{owner}/{repo}/contents/{path}", headers=headers, params={"ref": ref} if ref else None)
        if res.status_code != 200:
            raise UpstreamError(f"GitHub returned {res.status_code} while reading {path}")
        return res.content

    async def list_issues(self, owner: str, repo: str):
        return await self._mcp.call_tool_json("list_issues", {"owner": owner, "repo": repo})

    async def list_commits(self, owner: str, repo: str, per_page: int = 30):
        return await self._mcp.call_tool_json("list_commits", {"owner": owner, "repo": repo, "perPage": per_page})

    async def list_pull_requests(self, owner: str, repo: str):
        return await self._mcp.call_tool_json("list_pull_requests", {"owner": owner, "repo": repo, "state": "open"})

    # Generic access used by the LLM agent loop and approved actions
    async def list_tools(self) -> list[ToolSpec]:
        return await self._mcp.list_tools()

    async def call_tool(self, name: str, args: dict) -> str:
        return await self._mcp.call_tool(name, args)
