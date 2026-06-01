from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.runs import router as runs_router
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    summary="Full-stack demo API for LLM evaluation, RAG, and observability workflows.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Return a lightweight health signal for local demos and compose checks."""

    return {
        "status": "ok",
        "environment": settings.environment,
        "provider_mode": settings.provider_mode,
    }
