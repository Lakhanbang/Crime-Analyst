"""Prediction service placeholder for future joblib/scikit-learn integration."""

from __future__ import annotations

from app.models.schemas import PredictionRequest


class PredictionService:
    """Service contract reserved for future ML model loading and inference."""

    def predict(self, request: PredictionRequest) -> dict[str, object]:
        """Return a stable placeholder response until a trained model is added."""

        return {
            "status": "not_ready",
            "message": (
                "Prediction model is not loaded yet. Connect a trained joblib artifact "
                "to enable forecasts."
            ),
            "requested_input": request,
            "prediction": None,
        }
