"""Any git host (Bitbucket, Azure DevOps, Gitea, self-hosted, ssh...) via a cached shallow clone and `git` plumbing.
No pull requests: those need a host-specific API."""
from app.core.config import settings
from app.core.exceptions import BadRequestError, NotFoundError, UpstreamError
from app.models.repo_ref_model import RepoRef
from app.providers.base_git_provider import BaseGitProvider
from app.providers.git_cli import GitCli
from app.repositories.repo_link_registry import RepoLinkRegistry
from app.schemas.commit_schemas import CommitResponse
from app.schemas.repository_schemas import ContentEntryResponse, FileResponse, RepositoryDetailResponse
from app.utils.file_content import MAX_IMAGE_BYTES, MAX_TEXT_CHARS, blob_response, is_image
from app.utils.language_detect import detect_language
from app.utils.web_urls import commit_url, file_url, web_base


class GenericGitProvider(BaseGitProvider):
    kind = "git"
    supports_pull_requests = False

    def __init__(self, registry: RepoLinkRegistry, git: GitCli | None = None) -> None:
        self._registry = registry
        self._git = git or GitCli()

    async def _repo(self, ref: RepoRef):
        clone_url = self._registry.clone_url(ref.id) or f"https://{ref.host}/{ref.path}.git"
        return await self._git.ensure_clone(clone_url, settings.git_host_tokens.get(ref.host))

    @staticmethod
    def _check_path(path: str) -> None:
        if any(p == ".." for p in path.split("/")) or path.startswith("-"):
            raise BadRequestError("Invalid path.")

    async def get_repository(self, ref: RepoRef) -> RepositoryDetailResponse:
        repo = await self._repo(ref)
        branch = (await self._git.run(["symbolic-ref", "--short", "HEAD"], cwd=repo)).decode().strip() or None
        language = None
        try:
            names = (await self._git.run(["ls-tree", "-r", "--name-only", "HEAD"], cwd=repo, cap=2_000_000)).decode(errors="replace").splitlines()
            language = detect_language(names[:20000])
        except UpstreamError:
            pass
        return RepositoryDetailResponse(
            id=ref.id,
            provider=self.kind,
            supports_pull_requests=False,
            full_name=ref.path,
            description=None,
            private=False,
            default_branch=branch,
            language=language,
            html_url=web_base(ref),
        )

    async def list_contents(self, ref: RepoRef, path: str, branch: str | None) -> list[ContentEntryResponse]:
        self._check_path(path)
        repo = await self._repo(ref)
        rev = await self._git.resolve_rev(repo, branch)
        spec = f"{rev}:{path}" if path else rev
        try:
            out = await self._git.run(["ls-tree", "-z", spec], cwd=repo)
        except UpstreamError as exc:
            msg = exc.message.lower()
            if "not a tree" in msg:
                raise BadRequestError("Path is a file, not a directory") from exc
            if "not a valid object" in msg or "does not exist" in msg:
                raise NotFoundError(f"'{path}' was not found.") from exc
            raise
        entries = []
        for rec in out.decode(errors="replace").split("\0"):
            if not rec:
                continue
            meta, _, name = rec.partition("\t")
            kind = meta.split()[1]
            if kind in {"blob", "tree"}:
                entries.append(ContentEntryResponse(name=name, path=f"{path}/{name}".lstrip("/"), type="dir" if kind == "tree" else "file"))
        return entries

    async def read_file(self, ref: RepoRef, path: str, branch: str | None) -> FileResponse:
        self._check_path(path)
        if not path:
            raise BadRequestError("A file path is required.")
        repo = await self._repo(ref)
        rev = await self._git.resolve_rev(repo, branch)
        spec = f"{rev}:{path}"
        try:
            kind = (await self._git.run(["cat-file", "-t", spec], cwd=repo)).decode().strip()
        except UpstreamError as exc:
            raise NotFoundError(f"'{path}' was not found.") from exc
        if kind == "tree":
            raise BadRequestError("Path is a directory, not a file")
        cap = (MAX_IMAGE_BYTES if is_image(path) else MAX_TEXT_CHARS * 4) + 1
        blob = await self._git.run(["cat-file", "blob", spec], cwd=repo, cap=cap)
        branch_name = branch or (await self._git.run(["symbolic-ref", "--short", "HEAD"], cwd=repo)).decode().strip() or "HEAD"
        return blob_response(path, blob, file_url(ref, branch_name, path))

    async def list_commits(self, ref: RepoRef, limit: int) -> list[CommitResponse]:
        repo = await self._repo(ref)
        out = await self._git.run(["log", "-n", str(limit), "--format=%H%x1f%an%x1f%aI%x1f%B%x1e", "HEAD"], cwd=repo)
        commits = []
        for rec in out.decode(errors="replace").split("\x1e"):
            rec = rec.strip("\n")
            if not rec.strip():
                continue
            sha, author, date, message = (rec.split("\x1f", 3) + ["", "", ""])[:4]
            commits.append(CommitResponse(sha=sha, message=message.strip(), author_name=author or "Unknown", date=date or None, html_url=commit_url(ref, sha)))
        return commits
