from app.models.repo_ref_model import RepoRef
from app.providers.provider_factory import ProviderFactory
from app.repositories.github_repository import GitHubRepository
from app.schemas.issue_schemas import IssueResponse, PullRequestResponse


class IssueService:
    def __init__(self, github: GitHubRepository, providers: ProviderFactory) -> None:
        self._github = github
        self._providers = providers

    async def list_open_issues(self, owner: str, repo: str) -> list[IssueResponse]:
        """GitHub issues (other hosts: the AI reads them through its own tools)."""
        data = await self._github.list_issues(owner, repo)
        items = data.get("issues", data) if isinstance(data, dict) else data
        if not isinstance(items, list):
            return []
        return [IssueResponse(**i) for i in items if str(i.get("state", "open")).lower() == "open"]

    async def list_open_pull_requests(self, repo: str) -> list[PullRequestResponse]:
        """Pull requests (GitHub) / merge requests (GitLab); empty for hosts without an API integration."""
        ref = RepoRef.from_id(repo)
        return await (await self._providers.for_ref(ref)).list_pull_requests(ref)
