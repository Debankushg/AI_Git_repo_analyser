"""The agent loop: LLM decides -> we run tools -> results go back to the LLM -> repeat."""
import logging

from app.core.config import settings
from app.llm.base_llm_provider import BaseLLMProvider
from app.llm.prompts.repo_assistant_prompt import build_system_prompt
from app.mcp_layer import tool_policy
from app.models.chat_model import AgentResult, ConversationMessage
from app.models.repo_ref_model import RepoRef
from app.models.tool_model import ToolCall, ToolResult
from app.providers.provider_factory import ProviderFactory
from app.repositories.github_repository import GitHubRepository
from app.services.approval_service import ApprovalService
from app.services.tool_sources import McpToolSource, ProviderToolSource, ToolSource

log = logging.getLogger(__name__)


class ChatService:
    def __init__(self, llm: BaseLLMProvider, github: GitHubRepository, approvals: ApprovalService, providers: ProviderFactory) -> None:
        self._llm = llm
        self._github = github
        self._approvals = approvals
        self._providers = providers

    async def _tool_source(self, repo: str) -> ToolSource:
        ref = RepoRef.from_id(repo)
        provider = await self._providers.for_ref(ref)
        return McpToolSource(self._github) if provider.kind == "github" else ProviderToolSource(provider, ref)

    async def run(self, repo: str, messages: list[ConversationMessage]) -> AgentResult:
        source = await self._tool_source(repo)
        session = self._llm.new_session(build_system_prompt(repo, source.can_write), messages, await source.list_tools())
        result = AgentResult(reply="")

        for _ in range(settings.max_agent_rounds):
            turn = await session.generate()
            result.reply = turn.text
            if not turn.tool_calls:
                break
            session.add_tool_results([await self._execute(source, call, result) for call in turn.tool_calls])
        return result

    async def _execute(self, source: ToolSource, call: ToolCall, result: AgentResult) -> ToolResult:
        result.tool_calls.append(call.name)
        if source.can_write and tool_policy.is_write_tool(call.name):
            action = self._approvals.queue(call.name, tool_policy.apply_safety_defaults(call.name, call.args))
            result.pending_actions.append(action)
            return ToolResult(call.name, f"Queued for user approval (id {action.id}). Not executed yet.")
        try:
            return ToolResult(call.name, (await source.call(call.name, call.args))[:20000])
        except Exception as exc:  # let the model see tool errors and adapt
            log.warning("Tool %s failed: %s", call.name, exc)
            return ToolResult(call.name, f"Error: {exc}")
