from dataclasses import dataclass, field
from typing import Literal

from app.models.pending_action_model import PendingActionModel


@dataclass
class ConversationMessage:
    role: Literal["user", "assistant"]
    content: str


@dataclass
class AgentResult:
    reply: str
    tool_calls: list[str] = field(default_factory=list)
    pending_actions: list[PendingActionModel] = field(default_factory=list)
