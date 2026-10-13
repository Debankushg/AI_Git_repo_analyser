"""Remembers the exact clone URL (possibly with credentials the user pasted) for repositories opened from a link.
In memory only: never logged, never returned by the API."""


class RepoLinkRegistry:
    def __init__(self) -> None:
        self._clone_urls: dict[str, str] = {}

    def remember(self, repo_id: str, clone_url: str) -> None:
        self._clone_urls[repo_id] = clone_url

    def clone_url(self, repo_id: str) -> str | None:
        return self._clone_urls.get(repo_id)
