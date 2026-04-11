"""National analytics endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import NationalAnalyticsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/national",
    response_model=NationalAnalyticsResponse,
    summary="Get India-level crime analytics",
)
def get_national_analytics() -> NationalAnalyticsResponse:
    """Return India-wide totals, rankings, and yearly trends."""

    service = AnalyticsService.from_cache()
    return NationalAnalyticsResponse(**service.get_national_analytics())
