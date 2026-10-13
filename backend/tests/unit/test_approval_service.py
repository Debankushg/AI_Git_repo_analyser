import pytest

from app.core.exceptions import NotFoundError
from app.repositories.action_repository import ActionRepository
from app.services.approval_service import ApprovalService


class FakeGitHub:
    async def call_tool(self, name, args):
        return "created"


@pytest.mark.asyncio
async def test_approve_executes_and_marks_approved():
    svc = ApprovalService(ActionRepository(), FakeGitHub())
    action = svc.queue("create_issue", {"title": "Bug"})
    done = await svc.approve(action.id)
    assert done.status == "approved" and done.result == "created"
    with pytest.raises(NotFoundError):
        svc.reject(action.id)
