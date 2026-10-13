from app.schemas.issue_schemas import IssueResponse, PullRequestResponse
from app.services.issue_service import IssueService


class IssueController:
    def __init__(self, service: IssueService) -> None:
        self._service = service

    async def list_issues(self, owner: str, repo: str) -> list[IssueResponse]:
        return await self._service.list_open_issues(owner, repo)

    async def list_pull_requests(self, repo: str) -> list[PullRequestResponse]:
        return await self._service.list_open_pull_requests(repo)
