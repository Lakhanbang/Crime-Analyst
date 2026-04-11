"""Model loading and recursive future prediction utilities."""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd

from config import get_settings
from features import build_future_frame, create_training_features


def load_best_model(model_path: str | Path | None = None) -> dict[str, object]:
    """Load the persisted best model bundle."""

    settings = get_settings()
    target_path = Path(model_path) if model_path else settings.best_model_path
    if not target_path.exists():
        raise FileNotFoundError(f"Best model file not found: {target_path}")
    return joblib.load(target_path)


def _iterative_forecast(bundle: dict[str, object], target_year: int) -> pd.DataFrame:
    """Generate recursive predictions up to the requested year."""

    history_df = bundle["history_df"].copy()
    model = bundle["model"]
    preprocessor = bundle["preprocessor"]
    feature_columns = bundle["feature_columns"]
    last_actual_year = int(history_df["year"].max())

    if target_year <= last_actual_year:
        return history_df[history_df["year"] == target_year].copy()

    for year in range(last_actual_year + 1, target_year + 1):
        future_base = build_future_frame(history_df, year)
        combined = pd.concat([history_df, future_base], ignore_index=True)
        engineered = create_training_features(combined)
        future_features = engineered[engineered["year"] == year].copy()

        transformed = preprocessor.transform(future_features[feature_columns])
        predictions = model.predict(transformed)
        future_base["cases_reported"] = predictions
        history_df = pd.concat([history_df, future_base], ignore_index=True)

    return history_df[history_df["year"] == target_year].copy()


def predict_future(state: str, crime_type: str, year: int) -> dict[str, object]:
    """Predict the crime total for a single state and crime type in a future year."""

    bundle = load_best_model()
    forecast_df = _iterative_forecast(bundle, year)

    mask = (
        forecast_df["state"].str.casefold().eq(state.strip().casefold())
        & forecast_df["crime_type"].str.casefold().eq(crime_type.strip().casefold())
    )
    matched = forecast_df.loc[mask]
    if matched.empty:
        raise ValueError(f"No state/crime combination found for state='{state}', crime_type='{crime_type}'")

    row = matched.iloc[0]
    return {
        "state": str(row["state"]),
        "crime_type": str(row["crime_type"]),
        "year": int(year),
        "predicted_cases": float(row["cases_reported"]),
        "model_name": str(bundle["model_name"]),
    }
