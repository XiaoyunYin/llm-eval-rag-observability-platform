from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    summary="Minimal portfolio implementation for LLM evaluation, RAG, and observability.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Return a lightweight health signal for local demos and compose checks."""

    return {
        "status": "ok",
        "environment": settings.environment,
        "provider_mode": settings.provider_mode,
    }
