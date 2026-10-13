"""Safe wrapper around the `git` CLI: shallow bare clones in a cache dir, read-only plumbing commands.

Safety: only https/http/ssh transports (GIT_ALLOW_PROTOCOL), no prompts (GIT_TERMINAL_PROMPT=0, ssh BatchMode),
timeouts, size caps, and credentials are scrubbed from every error message."""
import asyncio
import hashlib
import os
import re
import shutil
import tempfile
import time
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import BadRequestError, NotFoundError, UpstreamError

_SAFE_REF = re.compile(r"^[A-Za-z0-9][\w./+-]{0,200}$")
_SAFE_URL = re.compile(r"^(https?://|ssh://|[\w.-]+@[\w.-]+:)", re.I)


def _env() -> dict:
    return {
        **os.environ,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_ALLOW_PROTOCOL": "https:http:ssh",
        "GIT_SSH_COMMAND": "ssh -o BatchMode=yes",
        "GIT_CONFIG_NOSYSTEM": "1",
        "LC_ALL": "C",
    }


def _scrub(text: str, secrets: list[str]) -> str:
    for s in secrets:
        if s:
            text = text.replace(s, "***")
    return re.sub(r"(https?://)[^/@\s]+@", r"\1***@", text)


class GitCli:
    def __init__(self) -> None:
        base = settings.git_cache_dir or os.path.join(tempfile.gettempdir(), "repo-assistant-clones")
        self._root = Path(base)
        self._locks: dict[str, asyncio.Lock] = {}

    async def run(self, args: list[str], cwd: Path | None = None, timeout: int = 60, cap: int | None = None, secrets: list[str] | None = None) -> bytes:
        """Run git; optionally read at most `cap` bytes of stdout (then stop the process)."""
        try:
            proc = await asyncio.create_subprocess_exec(
                "git", "-c", "protocol.file.allow=never", "-c", "protocol.ext.allow=never", *args,
                cwd=str(cwd) if cwd else None, env=_env(), stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise UpstreamError("git is not installed on the server.") from exc
        try:
            if cap is not None:
                out = await asyncio.wait_for(proc.stdout.read(cap), timeout)
                if len(out) >= cap:
                    proc.kill()
                await proc.wait()
                return out
            out, err = await asyncio.wait_for(proc.communicate(), timeout)
        except asyncio.TimeoutError as exc:
            proc.kill()
            raise UpstreamError("git timed out (repository too large or host unreachable).") from exc
        if proc.returncode != 0:
            raise UpstreamError(_scrub(err.decode(errors="replace").strip().splitlines()[-1] if err.strip() else "git failed", secrets or []))
        return out

    def _cache_path(self, clone_url: str) -> Path:
        key = hashlib.sha256(re.sub(r"//[^/@]*@", "//", clone_url).encode()).hexdigest()[:20]
        return self._root / key

    async def ensure_clone(self, clone_url: str, token: str | None = None) -> Path:
        """Shallow bare clone (cached for git_cache_ttl_seconds)."""
        if not _SAFE_URL.match(clone_url) or clone_url.startswith("-"):
            raise BadRequestError("Unsupported clone URL.")
        target = self._cache_path(clone_url)
        lock = self._locks.setdefault(str(target), asyncio.Lock())
        async with lock:
            if target.exists() and time.time() - target.stat().st_mtime < settings.git_cache_ttl_seconds:
                return target
            shutil.rmtree(target, ignore_errors=True)
            self._root.mkdir(parents=True, exist_ok=True)
            url = clone_url
            if token and url.lower().startswith("https://") and "@" not in url.split("/")[2]:
                url = url.replace("https://", f"https://oauth2:{token}@", 1)
            try:
                await self.run(
                    ["clone", "--bare", "--depth", str(settings.git_clone_depth), "--single-branch", "--no-tags", "--", url, str(target)],
                    timeout=settings.git_clone_timeout_seconds, secrets=[token or ""],
                )
            except UpstreamError as exc:
                shutil.rmtree(target, ignore_errors=True)
                msg = exc.message.lower()
                if "not found" in msg or "does not exist" in msg or "repository" in msg and "not" in msg:
                    raise NotFoundError("Repository not found, or it is private (add a token in GIT_HOST_TOKENS or use an ssh link).") from exc
                if "authentication" in msg or "denied" in msg or "could not read" in msg:
                    raise UpstreamError("Access denied. For private repositories add a token in GIT_HOST_TOKENS or paste an ssh link.") from exc
                raise
            return target

    async def resolve_rev(self, repo: Path, branch: str | None) -> str:
        """Return a safe revision name, fetching the branch/tag on demand."""
        if not branch:
            return "HEAD"
        if not _SAFE_REF.match(branch) or ".." in branch:
            raise BadRequestError("Invalid branch or tag name.")
        async def exists() -> bool:
            try:
                await self.run(["rev-parse", "--verify", "--quiet", f"{branch}^{{commit}}"], cwd=repo)
                return True
            except UpstreamError:
                return False
        if await exists():
            return branch
        for refspec in (f"+refs/heads/{branch}:refs/heads/{branch}", f"+refs/tags/{branch}:refs/tags/{branch}"):
            try:
                await self.run(["fetch", "--depth", str(settings.git_clone_depth), "--no-tags", "origin", refspec], cwd=repo, timeout=settings.git_clone_timeout_seconds)
                if await exists():
                    return branch
            except UpstreamError:
                continue
        raise NotFoundError(f"Branch or tag '{branch}' was not found.")
