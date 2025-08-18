import time

from app.api.v1.router import api_router
from app.config.logger import get_logger, setup_logging
from app.config.settings import settings
from fastapi import FastAPI

setup_logging(log_level=settings.log_level, log_format=settings.log_format)

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description=settings.description,
    version=settings.app_version,
    docs_url=settings.docs_url,
    redoc_url=settings.redoc_url,
    openapi_url=settings.openapi_url,
)

app.include_router(api_router, prefix=f"{settings.api_prefix}")


@app.get("/", tags=["Info"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "docs_url": settings.docs_url,
        "redocs_url": settings.redoc_url,
        "health_check": "/health",
    }


@app.get("/version", tags=["Info"])
async def get_version():
    """Get application version information."""
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": time.time(),
    }
