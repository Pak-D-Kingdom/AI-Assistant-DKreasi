from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.core.config import get_settings
from app.core.logging import logger
from app.db.database import init_db
from app.api.v1.chat import router as chat_router
from app.api.v1.health import router as health_router
from app.api.v1.sites import router as sites_router
from app.api.v1.ingest import router as ingest_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database and AI Engine...")
    await init_db()
    yield
    logger.info("Shutting down AI Engine...")


app = FastAPI(
    title=settings.APP_NAME,
    description="PakDe Group Central AI Engine & Multi-Tier Assistant Backend",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(sites_router, prefix="/api/v1")
app.include_router(ingest_router, prefix="/api/v1")

# Also mount chat directly at root for convenience (POST /v1/chat & POST /api/ai/chat)
app.include_router(chat_router, prefix="")

# Mount static widget if folder exists
widget_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "widget")
if os.path.exists(widget_dir):
    app.mount("/widget", StaticFiles(directory=widget_dir), name="widget")


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "online",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
