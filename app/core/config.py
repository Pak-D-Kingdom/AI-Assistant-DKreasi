from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "ai-assistant-dkreasi"
    APP_ENV: str = "local"
    DEBUG: bool = True
    PORT: int = 8001
    HOST: str = "0.0.0.0"

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:8001,http://127.0.0.1:8001,http://localhost:8002,http://127.0.0.1:8002,http://localhost:8003,http://127.0.0.1:8003,http://localhost:3000,https://webia.id,https://d-kreasi.com,https://dkarsa.id"

    # LLM Settings
    AI_PROVIDER: str = "mock"  # llm, gemini, mock
    LLM_BASE_URL: str = "http://localhost:20128/v1"
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "Nasikotak"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 2048
    LLM_TIMEOUT: int = 30

    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # Database & Storage
    DATABASE_URL: str = "sqlite+aiosqlite:///data/app.db"
    FAISS_BASE_PATH: str = "data/faiss_index"
    EMBEDDING_MODEL: str = "intfloat/multilingual-e5-small"

    # Customer Support WhatsApp Handoff
    AI_CS_WHATSAPP: str = "6281234567890"
    AI_CS_DEFAULT_MESSAGE: str = "Halo CS PakDe Group, saya ingin berkonsultasi mengenai layanan D-KREASI."

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
