"""GitLab (gitlab.com and self-hosted) through its REST API v4. Nested groups supported."""
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.core.exceptions import BadRequestError, NotFoundError, UpstreamError
from app.models.repo_ref_model import RepoRef
from app.providers.base_git_provider import BaseGitProvider
from app.schemas.commit_schemas import CommitResponse
from app.schemas.issue_schemas import PullRequestResponse
from app.schemas.repository_schemas import ContentEntryResponse, FileResponse, RepositoryDetailResponse
from app.utils.file_content import blob_response
from app.utils.web_urls import file_url


class GitLabProvider(BaseGitProvider):
    kind = "gitlab"
    pull_request_label = "Merge requests"

    async def _get(self, ref: RepoRef, path: str, params: dict | None = None) -> httpx.Response:
        params = {k: v for k, v in (params or {}).items() if v not in (None, "")}  # GitLab treats an empty ref= as "not found"
        headers = {}
        if token := settings.git_host_tokens.get(ref.host):
            headers["PRIVATE-TOKEN"] = token
        try:
            async with httpx.AsyncClient(timeout=20, follow_redirects=True) as http:
                res = await http.get(f"https://{ref.host}/api/v4{path}", headers=headers, params=params)
        except httpx.HTTPError as exc:
            raise UpstreamError(f"Could not reach {ref.host}: {exc.__class__.__name__}") from exc
        if res.status_code == 404:
            raise NotFoundError("Not found on GitLab (wrong path/branch, or the project is private: set GIT_HOST_TOKENS).")
        if res.status_code in (401, 403):
            raise UpstreamError(f"{ref.host} rejected the request. Add a token for this host in GIT_HOST_TOKENS.")
        if res.status_code >= 400:
            raise UpstreamError(f"{ref.host} returned {res.status_code}")
        return res

    @staticmethod
    def _pid(ref: RepoRef) -> str:
        return f"/projects/{quote(ref.path, safe='')}"

    async def get_repository(self, ref: RepoRef) -> RepositoryDetailResponse:
        p = (await self._get(ref, self._pid(ref))).json()
        language = None
        try:
            langs = (await self._get(ref, f"{self._pid(ref)}/languages")).json()
            language = max(langs, key=langs.get) if langs else None
        except Exception:  # languages are optional
            pass
        return RepositoryDetailResponse(
            id=f"{ref.host}/{p['path_with_namespace']}",
            provider=self.kind,
            pull_request_label=self.pull_request_label,
            full_name=p["path_with_namespace"],
            description=p.get("description"),
            private=p.get("visibility", "public") != "public",
            default_branch=p.get("default_branch"),
            language=language,
            stars=p.get("star_count", 0),
            forks=p.get("forks_count", 0),
            open_issues=p.get("open_issues_count", 0),
            html_url=p.get("web_url"),
            owner_avatar_url=p.get("avatar_url") or (p.get("namespace") or {}).get("avatar_url"),
        )

    async def _default_branch(self, ref: RepoRef) -> str:
        return (await self._get(ref, self._pid(ref))).json().get("default_branch") or "HEAD"

    async def list_contents(self, ref: RepoRef, path: str, branch: str | None) -> list[ContentEntryResponse]:
        entries: list[dict] = []
        page = "1"
        for _ in range(5):  # up to 500 entries
            res = await self._get(ref, f"{self._pid(ref)}/repository/tree", {"path": path, "ref": branch, "per_page": 100, "page": page})
            entries += res.json()
            page = res.headers.get("x-next-page", "")
            if not page:
                break
        if not entries and path:
            raise BadRequestError("Path is a file, not a directory")
        return [ContentEntryResponse(name=e["name"], path=e["path"], type="dir" if e["type"] == "tree" else "file") for e in entries if e["type"] in {"tree", "blob"}]

    async def read_file(self, ref: RepoRef, path: str, branch: str | None) -> FileResponse:
        branch = branch or await self._default_branch(ref)
        res = await self._get(ref, f"{self._pid(ref)}/repository/files/{quote(path, safe='')}/raw", {"ref": branch})
        return blob_response(path, res.content, file_url(ref, branch, path))

    async def list_commits(self, ref: RepoRef, limit: int) -> list[CommitResponse]:
        data = (await self._get(ref, f"{self._pid(ref)}/repository/commits", {"per_page": limit})).json()
        return [
            CommitResponse(
                sha=c["id"],
                message=c.get("message") or c.get("title", ""),
                author_name=c.get("author_name", "Unknown"),
                date=c.get("authored_date") or c.get("created_at"),
                html_url=c.get("web_url"),
            )
            for c in data
        ]

    async def list_pull_requests(self, ref: RepoRef) -> list[PullRequestResponse]:
        data = (await self._get(ref, f"{self._pid(ref)}/merge_requests", {"state": "opened", "per_page": 30})).json()
        return [
            PullRequestResponse(
                number=m["iid"],
                title=m["title"],
                draft=bool(m.get("draft") or m.get("work_in_progress")),
                html_url=m.get("web_url"),
                user={"login": (m.get("author") or {}).get("username"), "avatar_url": (m.get("author") or {}).get("avatar_url")},
                created_at=m.get("created_at"),
            )
            for m in data
        ]
