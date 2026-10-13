from fastapi import APIRouter, Depends

from app.controllers.issue_controller import IssueController
from app.core.dependencies import get_issue_controller
from app.schemas.issue_schemas import IssueResponse, PullRequestResponse

router = APIRouter(prefix="/repositories", tags=["issues"])


@router.get("/pulls", response_model=list[PullRequestResponse])
async def list_pulls(repo: str, ctrl: IssueController = Depends(get_issue_controller)):
    """Open pull requests (GitHub) / merge requests (GitLab). Empty for hosts without an API integration."""
    return await ctrl.list_pull_requests(repo)


@router.get("/{owner}/{repo}/issues", response_model=list[IssueResponse])
async def list_issues(owner: str, repo: str, ctrl: IssueController = Depends(get_issue_controller)):
    """Open issues (GitHub repositories)."""
    return await ctrl.list_issues(owner, repo)
