"""One interface for every git host. Services only talk to this, so adding a host = adding one provider file."""
from abc import ABC, abstractmethod

from app.models.repo_ref_model import RepoRef
from app.schemas.commit_schemas import CommitResponse
from app.schemas.issue_schemas import PullRequestResponse
from app.schemas.repository_schemas import ContentEntryResponse, FileResponse, RepositoryDetailResponse


class BaseGitProvider(ABC):
    kind: str  # github | gitlab | git
    supports_pull_requests: bool = True
    pull_request_label: str = "Pull requests"

    @abstractmethod
    async def get_repository(self, ref: RepoRef) -> RepositoryDetailResponse: ...

    @abstractmethod
    async def list_contents(self, ref: RepoRef, path: str, branch: str | None) -> list[ContentEntryResponse]: ...

    @abstractmethod
    async def read_file(self, ref: RepoRef, path: str, branch: str | None) -> FileResponse: ...

    @abstractmethod
    async def list_commits(self, ref: RepoRef, limit: int) -> list[CommitResponse]: ...

    async def list_pull_requests(self, ref: RepoRef) -> list[PullRequestResponse]:
        return []
