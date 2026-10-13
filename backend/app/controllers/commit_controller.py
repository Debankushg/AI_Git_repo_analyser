from app.schemas.commit_schemas import CommitResponse
from app.services.commit_service import CommitService


class CommitController:
    def __init__(self, service: CommitService) -> None:
        self._service = service

    async def list_commits(self, repo: str, limit: int) -> list[CommitResponse]:
        return await self._service.list_commits(repo, limit)
