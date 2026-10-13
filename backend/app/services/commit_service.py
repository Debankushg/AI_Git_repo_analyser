from app.models.repo_ref_model import RepoRef
from app.providers.provider_factory import ProviderFactory
from app.schemas.commit_schemas import CommitResponse


class CommitService:
    def __init__(self, providers: ProviderFactory) -> None:
        self._providers = providers

    async def list_commits(self, repo: str, limit: int = 30) -> list[CommitResponse]:
        ref = RepoRef.from_id(repo)
        return await (await self._providers.for_ref(ref)).list_commits(ref, limit)
