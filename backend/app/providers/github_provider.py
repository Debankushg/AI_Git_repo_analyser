"""GitHub via the GitHub MCP server (REST only for metadata and binary files the MCP server can't carry)."""
import base64
import binascii
import json
import re

from app.core.exceptions import BadRequestError
from app.models.repo_ref_model import RepoRef
from app.providers.base_git_provider import BaseGitProvider
from app.repositories.github_repository import GitHubRepository
from app.schemas.commit_schemas import CommitResponse
from app.schemas.issue_schemas import PullRequestResponse
from app.schemas.repository_schemas import ContentEntryResponse, FileResponse, RepositoryDetailResponse
from app.utils.file_content import blob_response, is_image, text_response
from app.utils.web_urls import file_url

_B64 = re.compile(r"[A-Za-z0-9+/]+={0,2}")


class GitHubProvider(BaseGitProvider):
    kind = "github"

    def __init__(self, github: GitHubRepository) -> None:
        self._github = github

    async def get_repository(self, ref: RepoRef) -> RepositoryDetailResponse:
        r = await self._github.get_repository_info(ref.owner, ref.name)
        return RepositoryDetailResponse(
            id=r["full_name"],
            provider=self.kind,
            full_name=r["full_name"],
            description=r.get("description"),
            private=r.get("private", False),
            default_branch=r.get("default_branch"),
            language=r.get("language"),
            stars=r.get("stargazers_count", 0),
            forks=r.get("forks_count", 0),
            open_issues=r.get("open_issues_count", 0),
            html_url=r.get("html_url"),
            owner_avatar_url=(r.get("owner") or {}).get("avatar_url"),
        )

    async def list_contents(self, ref: RepoRef, path: str, branch: str | None) -> list[ContentEntryResponse]:
        data = await self._github.get_contents(ref.owner, ref.name, path, branch)
        if not isinstance(data, list):
            raise BadRequestError("Path is a file, not a directory")
        return [ContentEntryResponse(name=e["name"], path=e["path"], type=e["type"]) for e in data]

    async def read_file(self, ref: RepoRef, path: str, branch: str | None) -> FileResponse:
        web_url = file_url(ref, branch or "HEAD", path)
        if is_image(path):  # the MCP server UTF-8-decodes content, which corrupts binary data
            return blob_response(path, await self._github.get_raw_file(ref.owner, ref.name, path, branch), web_url)
        data = await self._github.get_contents(ref.owner, ref.name, path, branch)
        if isinstance(data, list):
            raise BadRequestError("Path is a directory, not a file")
        text = self._extract_text(data)
        size = data["size"] if isinstance(data, dict) and isinstance(data.get("size"), int) else None
        return text_response(path, text, size, web_url)

    @staticmethod
    def _extract_text(data) -> str:
        """The npx GitHub MCP server already decodes file content but still reports encoding='base64',
        so base64 is only decoded when the result is valid UTF-8 text."""
        if isinstance(data, dict):
            content = data.get("content")
            if content is None:
                return json.dumps(data, indent=2)  # a JSON file that was auto-parsed
            content = str(content)
            if data.get("encoding") == "base64":
                compact = "".join(content.split())
                if compact and len(compact) % 4 == 0 and _B64.fullmatch(compact):
                    try:
                        return base64.b64decode(compact, validate=True).decode("utf-8")
                    except (binascii.Error, UnicodeDecodeError):
                        pass
            return content
        if isinstance(data, list):
            return json.dumps(data, indent=2)
        return str(data)

    async def list_commits(self, ref: RepoRef, limit: int) -> list[CommitResponse]:
        data = await self._github.list_commits(ref.owner, ref.name, limit)
        if not isinstance(data, list):
            return []
        commits = []
        for c in data:
            git = c.get("commit", {})
            git_author = git.get("author") or {}
            gh_author = c.get("author") or {}  # null when the email isn't linked to a GitHub account
            commits.append(
                CommitResponse(
                    sha=c["sha"],
                    message=git.get("message", ""),
                    author_name=git_author.get("name") or gh_author.get("login") or "Unknown",
                    author_login=gh_author.get("login"),
                    avatar_url=gh_author.get("avatar_url"),
                    date=git_author.get("date"),
                    html_url=c.get("html_url"),
                )
            )
        return commits

    async def list_pull_requests(self, ref: RepoRef) -> list[PullRequestResponse]:
        data = await self._github.list_pull_requests(ref.owner, ref.name)
        return [PullRequestResponse(**p) for p in data] if isinstance(data, list) else []
