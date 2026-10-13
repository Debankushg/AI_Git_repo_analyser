"""Dependency wiring (composition root). Every layer gets its collaborators from here,
so swapping an implementation (e.g. a different LLM or a DB-backed action store) is a one-line change."""
from functools import lru_cache

from app.controllers.action_controller import ActionController
from app.controllers.chat_controller import ChatController
from app.controllers.commit_controller import CommitController
from app.controllers.issue_controller import IssueController
from app.controllers.meta_controller import MetaController
from app.controllers.repository_controller import RepositoryController
from app.llm.base_llm_provider import BaseLLMProvider
from app.llm.llm_factory import create_llm_provider
from app.mcp_layer.client.github_mcp_client import GitHubMCPClient
from app.providers.generic_git_provider import GenericGitProvider
from app.providers.github_provider import GitHubProvider
from app.providers.gitlab_provider import GitLabProvider
from app.providers.provider_factory import ProviderFactory
from app.repositories.action_repository import ActionRepository
from app.repositories.repo_link_registry import RepoLinkRegistry
from app.repositories.github_repository import GitHubRepository
from app.services.approval_service import ApprovalService
from app.services.chat_service import ChatService
from app.services.endpoint_catalog_service import EndpointCatalogService
from app.services.commit_service import CommitService
from app.services.issue_service import IssueService
from app.services.repository_service import RepositoryService


@lru_cache
def get_mcp_client() -> GitHubMCPClient:
    return GitHubMCPClient()


@lru_cache
def get_github_repository() -> GitHubRepository:
    return GitHubRepository(get_mcp_client())


@lru_cache
def get_repo_link_registry() -> RepoLinkRegistry:
    return RepoLinkRegistry()


@lru_cache
def get_provider_factory() -> ProviderFactory:
    return ProviderFactory(GitHubProvider(get_github_repository()), GitLabProvider(), GenericGitProvider(get_repo_link_registry()))


@lru_cache
def get_action_repository() -> ActionRepository:
    return ActionRepository()


@lru_cache
def get_llm_provider() -> BaseLLMProvider:
    return create_llm_provider()


@lru_cache
def get_approval_service() -> ApprovalService:
    return ApprovalService(get_action_repository(), get_github_repository())


@lru_cache
def get_chat_service() -> ChatService:
    return ChatService(get_llm_provider(), get_github_repository(), get_approval_service(), get_provider_factory())


@lru_cache
def get_repository_service() -> RepositoryService:
    return RepositoryService(get_provider_factory(), get_github_repository(), get_repo_link_registry())


@lru_cache
def get_issue_service() -> IssueService:
    return IssueService(get_github_repository(), get_provider_factory())


@lru_cache
def get_commit_service() -> CommitService:
    return CommitService(get_provider_factory())


def get_repository_controller() -> RepositoryController:
    return RepositoryController(get_repository_service())


def get_issue_controller() -> IssueController:
    return IssueController(get_issue_service())


def get_commit_controller() -> CommitController:
    return CommitController(get_commit_service())


def get_meta_controller() -> MetaController:
    return MetaController(EndpointCatalogService())


def get_chat_controller() -> ChatController:
    return ChatController(get_chat_service())


def get_action_controller() -> ActionController:
    return ActionController(get_approval_service())
