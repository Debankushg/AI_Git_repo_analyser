from fastapi import APIRouter, Depends, Query

from app.controllers.commit_controller import CommitController
from app.core.dependencies import get_commit_controller
from app.schemas.commit_schemas import CommitResponse

router = APIRouter(prefix="/repositories", tags=["commits"])


@router.get("/commits", response_model=list[CommitResponse])
async def list_commits(repo: str, limit: int = Query(30, ge=1, le=100), ctrl: CommitController = Depends(get_commit_controller)):
    return await ctrl.list_commits(repo, limit)
