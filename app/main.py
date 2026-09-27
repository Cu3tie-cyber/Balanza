from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    description="A reliability-focused fintech backend API.",
    version="0.1.0",
)

app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "environment": settings.environment,
    }