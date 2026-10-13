from app.schemas.repository_schemas import (
    ContentEntryResponse,
    FileResponse,
    RepositoryDetailResponse,
    RepositoryResponse,
    ResolveResponse,
)
from app.services.repository_service import RepositoryService


class RepositoryController:
    def __init__(self, service: RepositoryService) -> None:
        self._service = service

    async def list_repositories(self) -> list[RepositoryResponse]:
        return await self._service.list_repositories()

    async def resolve_link(self, url: str) -> ResolveResponse:
        return await self._service.resolve_link(url)

    async def get_detail(self, repo: str) -> RepositoryDetailResponse:
        return await self._service.get_detail(repo)

    async def list_contents(self, repo: str, path: str, ref: str | None) -> list[ContentEntryResponse]:
        return await self._service.list_contents(repo, path, ref)

    async def read_file(self, repo: str, path: str, ref: str | None) -> FileResponse:
        return await self._service.read_file(repo, path, ref)
