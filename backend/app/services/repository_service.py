from app.core.config import settings
from app.models.repo_ref_model import RepoRef
from app.providers.provider_factory import ProviderFactory
from app.repositories.github_repository import GitHubRepository
from app.repositories.repo_link_registry import RepoLinkRegistry
from app.schemas.repository_schemas import (
    ContentEntryResponse,
    FileResponse,
    LinkTarget,
    RepositoryDetailResponse,
    RepositoryResponse,
    ResolveResponse,
)
from app.utils.git_url_parser import parse_git_link


class RepositoryService:
    def __init__(self, providers: ProviderFactory, github: GitHubRepository, registry: RepoLinkRegistry) -> None:
        self._providers = providers
        self._github = github
        self._registry = registry

    async def list_repositories(self) -> list[RepositoryResponse]:
        """The configured GitHub user's repositories (for the dropdown)."""
        data = await self._github.search_repositories(f"user:{settings.github_username}")
        items = data.get("items", []) if isinstance(data, dict) else []
        return [RepositoryResponse(full_name=r["full_name"], description=r.get("description"), private=r.get("private", False)) for r in items]

    async def get_detail(self, repo: str) -> RepositoryDetailResponse:
        ref = RepoRef.from_id(repo)
        return await (await self._providers.for_ref(ref)).get_repository(ref)

    async def resolve_link(self, url: str) -> ResolveResponse:
        """Paste any git link: detect host, provider, repository and what the link points to."""
        parsed = parse_git_link(url)
        ref = RepoRef(parsed.host, parsed.path)
        self._registry.remember(ref.id, parsed.clone_url)
        detail = await (await self._providers.for_ref(ref)).get_repository(ref)
        if detail.id != ref.id:  # canonical id (e.g. GitHub's capitalisation)
            self._registry.remember(detail.id, parsed.clone_url)
        target = LinkTarget(kind=parsed.kind, ref=parsed.ref, path=parsed.file_path, number=parsed.number, sha=parsed.sha)
        return ResolveResponse(repository=detail, target=target)

    async def list_contents(self, repo: str, path: str, branch: str | None) -> list[ContentEntryResponse]:
        ref = RepoRef.from_id(repo)
        return await (await self._providers.for_ref(ref)).list_contents(ref, path, branch)

    async def read_file(self, repo: str, path: str, branch: str | None) -> FileResponse:
        ref = RepoRef.from_id(repo)
        return await (await self._providers.for_ref(ref)).read_file(ref, path, branch)
