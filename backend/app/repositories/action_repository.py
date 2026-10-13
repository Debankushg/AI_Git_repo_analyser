"""Storage for pending actions. In-memory for now; replace with a DB implementation later
without touching services (keep the same method names)."""
from app.models.pending_action_model import PendingActionModel


class ActionRepository:
    def __init__(self) -> None:
        self._items: dict[str, PendingActionModel] = {}

    def save(self, action: PendingActionModel) -> PendingActionModel:
        self._items[action.id] = action
        return action

    def get(self, action_id: str) -> PendingActionModel | None:
        return self._items.get(action_id)

    def list_by_status(self, status: str) -> list[PendingActionModel]:
        return [a for a in self._items.values() if a.status == status]
