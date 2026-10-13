from dataclasses import dataclass, field
from typing import Literal

ActionStatus = Literal["pending", "approved", "rejected"]


@dataclass
class PendingActionModel:
    """A write action (create issue / draft PR) proposed by the LLM, waiting for human approval."""

    id: str
    tool: str
    arguments: dict
    summary: str
    status: ActionStatus = "pending"
    result: str | None = None
