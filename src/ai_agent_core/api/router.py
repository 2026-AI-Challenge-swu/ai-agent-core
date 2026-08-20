from fastapi import APIRouter
from src.ai_agent_core.api.routes.health import router as health_router
from src.ai_agent_core.api.routes.chat import router as chat_router


api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(chat_router)