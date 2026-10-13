import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

log = logging.getLogger("request")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Adds an X-Request-ID header and logs method, path, status and duration."""

    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:8]
        start = time.perf_counter()
        response = await call_next(request)
        ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        log.info("%s %s %s %.0fms [%s]", request.method, request.url.path, response.status_code, ms, request_id)
        return response
