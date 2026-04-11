"""State-focused analytics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.models.schemas import StateCrimeAnalyticsResponse, StateListResponse, StateStatsResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/states", tags=["States"])


@router.get("", response_model=StateListResponse, summary="List all unique states")
def list_states() -> StateListResponse:
    """Return the set of available states from the cached dataset."""

    service = AnalyticsService.from_cache()
    states = service.list_states()
    return StateListResponse(total_states=len(states), states=states)


@router.get(
    "/{state}",
    response_model=StateStatsResponse,
    summary="Get aggregated analytics for a state",
)
def get_state_analytics(state: str) -> StateStatsResponse:
    """Return total cases, yearly trend, top crimes, and arrest averages for a state."""

    service = AnalyticsService.from_cache()
    try:
        return StateStatsResponse(**service.get_state_analytics(state))
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{state}/crime/{crime}",
    response_model=StateCrimeAnalyticsResponse,
    summary="Get state and crime specific analytics",
)
def get_state_crime_analytics(state: str, crime: str) -> StateCrimeAnalyticsResponse:
    """Return trend, totals, and recent growth for one crime type in one state."""

    service = AnalyticsService.from_cache()
    try:
        return StateCrimeAnalyticsResponse(**service.get_state_crime_analytics(state, crime))
    except LookupError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
