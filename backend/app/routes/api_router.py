from fastapi import APIRouter

from app.routes import action_routes, chat_routes, commit_routes, health_routes, issue_routes, meta_routes, repository_routes

api_router = APIRouter(prefix="/api")
for module in (health_routes, repository_routes, issue_routes, commit_routes, meta_routes, chat_routes, action_routes):
    api_router.include_router(module.router)
