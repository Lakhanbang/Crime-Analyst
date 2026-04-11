"""Crime category listing endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import CrimeListResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/crimes", tags=["Crimes"])


@router.get("", response_model=CrimeListResponse, summary="List all crime categories")
def list_crimes() -> CrimeListResponse:
    """Return all crime types available in the dataset."""

    service = AnalyticsService.from_cache()
    crimes = service.list_crimes()
    return CrimeListResponse(total_crime_types=len(crimes), crime_types=crimes)
