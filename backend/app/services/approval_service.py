import uuid

from app.core.exceptions import NotFoundError
from app.models.pending_action_model import PendingActionModel
from app.repositories.action_repository import ActionRepository
from app.repositories.github_repository import GitHubRepository


class ApprovalService:
    """Human-in-the-loop gate for write actions."""

    def __init__(self, actions: ActionRepository, github: GitHubRepository) -> None:
        self._actions = actions
        self._github = github

    def queue(self, tool: str, arguments: dict) -> PendingActionModel:
        title = arguments.get("title", "")
        action = PendingActionModel(
            id=uuid.uuid4().hex,
            tool=tool,
            arguments=arguments,
            summary=f"{tool.replace('_', ' ').title()}: {title}",
        )
        return self._actions.save(action)

    def list_pending(self) -> list[PendingActionModel]:
        return self._actions.list_by_status("pending")

    def _get_pending(self, action_id: str) -> PendingActionModel:
        action = self._actions.get(action_id)
        if not action or action.status != "pending":
            raise NotFoundError("No pending action with that id")
        return action

    async def approve(self, action_id: str) -> PendingActionModel:
        action = self._get_pending(action_id)
        action.result = await self._github.call_tool(action.tool, action.arguments)
        action.status = "approved"
        return self._actions.save(action)

    def reject(self, action_id: str) -> PendingActionModel:
        action = self._get_pending(action_id)
        action.status = "rejected"
        return self._actions.save(action)
