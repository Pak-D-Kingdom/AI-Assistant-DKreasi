"""
Entrypoint script for AI Assistant D-KREASI.
Run directly using: python main.py
"""
import uvicorn
from app.core.config import get_settings

if __name__ == "__main__":
    settings = get_settings()
    print(f"Starting {settings.APP_NAME} on http://localhost:{settings.PORT}")
    print(f"Swagger Documentation: http://localhost:{settings.PORT}/docs")
    print(f"Widget Testing UI: http://localhost:{settings.PORT}/widget/index.html")
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
