from fastapi import APIRouter, Depends

from app.controllers.repository_controller import RepositoryController
from app.core.dependencies import get_repository_controller
from app.schemas.repository_schemas import (
    ContentEntryResponse,
    FileResponse,
    RepositoryDetailResponse,
    RepositoryResponse,
    ResolveRequest,
    ResolveResponse,
)

router = APIRouter(prefix="/repositories", tags=["repositories"])

# `repo` is the repository id returned by /resolve: "owner/name" for GitHub, "host/group/name" for any other host.


@router.get("", response_model=list[RepositoryResponse])
async def list_repositories(ctrl: RepositoryController = Depends(get_repository_controller)):
    return await ctrl.list_repositories()


@router.post("/resolve", response_model=ResolveResponse)
async def resolve_repository_link(body: ResolveRequest, ctrl: RepositoryController = Depends(get_repository_controller)):
    """Parse a pasted git link (GitHub, GitLab, Bitbucket, Azure, self-hosted, ssh...) and detect the repository."""
    return await ctrl.resolve_link(body.url)


@router.get("/detail", response_model=RepositoryDetailResponse)
async def get_repository(repo: str, ctrl: RepositoryController = Depends(get_repository_controller)):
    return await ctrl.get_detail(repo)


@router.get("/contents", response_model=list[ContentEntryResponse])
async def list_contents(repo: str, path: str = "", ref: str | None = None, ctrl: RepositoryController = Depends(get_repository_controller)):
    return await ctrl.list_contents(repo, path, ref)


@router.get("/file", response_model=FileResponse)
async def read_file(repo: str, path: str, ref: str | None = None, ctrl: RepositoryController = Depends(get_repository_controller)):
    return await ctrl.read_file(repo, path, ref)
