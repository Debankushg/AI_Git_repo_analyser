"""Chooses the right provider for a repository's host."""
import httpx

from app.models.repo_ref_model import GITHUB_HOST, RepoRef
from app.providers.base_git_provider import BaseGitProvider
from app.providers.generic_git_provider import GenericGitProvider
from app.providers.github_provider import GitHubProvider
from app.providers.gitlab_provider import GitLabProvider

_GENERIC_ONLY = {"bitbucket.org", "dev.azure.com", "codeberg.org", "sourceforge.net"}


class ProviderFactory:
    def __init__(self, github: GitHubProvider, gitlab: GitLabProvider, generic: GenericGitProvider) -> None:
        self._github, self._gitlab, self._generic = github, gitlab, generic
        self._probed: dict[str, BaseGitProvider] = {}

    async def for_ref(self, ref: RepoRef) -> BaseGitProvider:
        host = ref.host
        if host == GITHUB_HOST:
            return self._github
        if host == "gitlab.com" or "gitlab" in host:
            return self._gitlab
        if host in _GENERIC_ONLY or host.endswith(".visualstudio.com"):
            return self._generic
        if host not in self._probed:  # unknown host: is it a self-hosted GitLab?
            self._probed[host] = self._gitlab if await self._looks_like_gitlab(host) else self._generic
        return self._probed[host]

    @staticmethod
    async def _looks_like_gitlab(host: str) -> bool:
        try:
            async with httpx.AsyncClient(timeout=4, follow_redirects=False) as http:
                res = await http.get(f"https://{host}/api/v4/version")
        except httpx.HTTPError:
            return False
        return any(k.lower().startswith("x-gitlab") for k in res.headers) or (res.status_code == 200 and "revision" in res.text)
