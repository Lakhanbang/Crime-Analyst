"""Prediction endpoint reserved for future ML integration."""

from __future__ import annotations

from fastapi import APIRouter

from app.models.schemas import PredictionRequest, PredictionResponse
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="", tags=["Predictions"])


@router.post("/predict", response_model=PredictionResponse, summary="Predict future crime values")
def predict(request: PredictionRequest) -> PredictionResponse:
    """Return a placeholder prediction response until an ML artifact is connected."""

    service = PredictionService()
    return PredictionResponse(**service.predict(request))
