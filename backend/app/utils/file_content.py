"""Shared logic that turns raw file data into the API's FileResponse (text / image / binary / truncated)."""
import base64
from pathlib import PurePosixPath

from app.schemas.repository_schemas import FileResponse

IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp", ".ico": "image/x-icon"}
MAX_TEXT_CHARS = 1_000_000
MAX_IMAGE_BYTES = 3_000_000


def is_image(path: str) -> bool:
    return PurePosixPath(path).suffix.lower() in IMAGE_TYPES


def image_response(path: str, blob: bytes, web_url: str | None = None) -> FileResponse:
    url = None
    if len(blob) <= MAX_IMAGE_BYTES:
        url = f"data:{IMAGE_TYPES[PurePosixPath(path).suffix.lower()]};base64,{base64.b64encode(blob).decode()}"
    return FileResponse(path=path, size=len(blob), is_binary=True, image_data_url=url, web_url=web_url)


def text_response(path: str, text: str, size: int | None = None, web_url: str | None = None) -> FileResponse:
    size = size if size is not None else len(text.encode())
    head = text[:8000]
    if "\x00" in head or head.count("�") > 20:
        return FileResponse(path=path, size=size, is_binary=True, web_url=web_url)  # binary data mangled into text
    return FileResponse(path=path, content=text[:MAX_TEXT_CHARS], size=size, truncated=len(text) > MAX_TEXT_CHARS, web_url=web_url)


def blob_response(path: str, blob: bytes, web_url: str | None = None) -> FileResponse:
    if is_image(path):
        return image_response(path, blob, web_url)
    return text_response(path, blob.decode("utf-8", errors="replace"), len(blob), web_url)
