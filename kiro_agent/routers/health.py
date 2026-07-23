"""Health check endpoint."""

from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()


@router.get("/health")
async def health_check():
    """Verifica que el backend está operativo."""
    return {
        "status": "healthy",
        "service": "kiro-backend-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
    }
