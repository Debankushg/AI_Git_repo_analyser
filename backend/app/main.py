from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.dependencies import get_mcp_client
from app.core.logging_config import setup_logging
from app.middlewares.error_handler_middleware import register_error_handlers
from app.middlewares.request_logging_middleware import RequestLoggingMiddleware
from app.routes.api_router import api_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    mcp = get_mcp_client()
    await mcp.start()  # launches the GitHub MCP server subprocess
    yield
    await mcp.stop()


def create_app() -> FastAPI:
    app = FastAPI(title="GitHub Repo Assistant", lifespan=lifespan)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"])
    register_error_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
