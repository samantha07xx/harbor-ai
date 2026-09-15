"""FastAPI application entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.retrieval import router as retrieval_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the Harbor API application."""

    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Backend API for Harbor, an Ontario healthcare navigation assistant.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    def health_check() -> dict[str, str]:
        return {
            "status": "ok",
            "service": "harbor-api",
            "environment": settings.environment,
        }

    app.include_router(chat_router, prefix="/api")
    app.include_router(retrieval_router, prefix="/api")
    return app


app = create_app()
