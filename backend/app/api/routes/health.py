from datetime import datetime, timezone

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """
    Basic health endpoint used by the frontend and deployment checks.
    """
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        timestamp_utc=datetime.now(timezone.utc),
    )