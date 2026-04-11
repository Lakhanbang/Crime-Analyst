"""Health-check route for service and dataset readiness."""

from __future__ import annotations

from fastapi import APIRouter

from app.config import get_settings
from app.loaders.csv_loader import get_dataset_metadata
from app.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", response_model=HealthResponse, summary="Check backend status")
def health_check() -> HealthResponse:
    """Return application and dataset readiness details."""

    settings = get_settings()
    metadata = get_dataset_metadata()
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        dataset_loaded=True,
        dataset=metadata,
    )
