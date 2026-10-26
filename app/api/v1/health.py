from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(tags=["Health"])
settings = get_settings()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "env": settings.APP_ENV,
        "gateway": "9router",
        "model": settings.LLM_MODEL,
    }
