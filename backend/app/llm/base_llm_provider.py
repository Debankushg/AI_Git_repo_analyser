"""Provider-neutral LLM interface. ChatService only depends on these classes,
so Gemini can be swapped for another model by adding one provider file."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from app.models.chat_model import ConversationMessage
from app.models.tool_model import ToolCall, ToolResult, ToolSpec


@dataclass
class LLMTurn:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)


class LLMSession(ABC):
    """One running conversation (keeps provider-specific history internally)."""

    @abstractmethod
    async def generate(self) -> LLMTurn: ...

    @abstractmethod
    def add_tool_results(self, results: list[ToolResult]) -> None: ...


class BaseLLMProvider(ABC):
    @abstractmethod
    def new_session(
        self, system_prompt: str, messages: list[ConversationMessage], tools: list[ToolSpec]
    ) -> LLMSession: ...
