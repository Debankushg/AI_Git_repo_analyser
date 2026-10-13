"""Domain errors. Services raise these; middlewares/error_handler_middleware.py turns them into HTTP responses."""


class AppError(Exception):
    status_code = 500

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    status_code = 404


class BadRequestError(AppError):
    status_code = 400


class RateLimitError(AppError):
    status_code = 429


class UpstreamError(AppError):
    """GitHub / MCP server / LLM provider failed."""

    status_code = 502
