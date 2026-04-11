"""Pydantic response and request schemas used across the API."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """API health response with dataset status."""

    status: str
    app_name: str
    version: str
    environment: str
    dataset_loaded: bool
    dataset: dict[str, object]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "ok",
                "app_name": "AI Crime Analytics Platform",
                "version": "1.0.0",
                "environment": "development",
                "dataset_loaded": True,
                "dataset": {
                    "rows": 65520,
                    "columns": ["year", "state", "crime_type", "number_of_cases"],
                    "year_range": {"start": 2000, "end": 2025},
                    "states_count": 36,
                    "crime_types_count": 15,
                    "csv_file": "D:/Projects/Crime_Analyst/Database/India_Crime_Dataset_StateWise_2000_2025.csv",
                },
            }
        }
    )


class MessageResponse(BaseModel):
    """Simple structured message response."""

    detail: str


class StateListResponse(BaseModel):
    """Response containing all available states."""

    total_states: int
    states: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_states": 3,
                "states": ["Delhi", "Rajasthan", "Uttar Pradesh"],
            }
        }
    )


class CrimeListResponse(BaseModel):
    """Response containing all available crime categories."""

    total_crime_types: int
    crime_types: list[str]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_crime_types": 4,
                "crime_types": ["Arson", "Burglary", "Fraud", "Murder"],
            }
        }
    )


class YearValuePoint(BaseModel):
    """Time-series point for yearly analytics."""

    year: int
    value: float = Field(..., description="Aggregated metric for the specified year")


class NamedMetric(BaseModel):
    """Name/value pair used for ranked analytics lists."""

    name: str
    value: float


class StateStatsResponse(BaseModel):
    """Aggregated analytics for a single state."""

    state: str
    total_cases: int
    total_arrests: int
    avg_arrests_per_record: float | None
    avg_charge_sheet_filed_pct: float | None
    avg_crime_rate_per_100k: float | None
    avg_police_response_time_min: float | None
    yearly_trend: list[YearValuePoint]
    top_crimes: list[NamedMetric]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "state": "Rajasthan",
                "total_cases": 450321,
                "total_arrests": 201340,
                "avg_arrests_per_record": 94.2,
                "avg_charge_sheet_filed_pct": 73.4,
                "avg_crime_rate_per_100k": 12.6,
                "avg_police_response_time_min": 48.7,
                "yearly_trend": [
                    {"year": 2023, "value": 17240},
                    {"year": 2024, "value": 17691},
                    {"year": 2025, "value": 18103},
                ],
                "top_crimes": [
                    {"name": "Murder", "value": 92110},
                    {"name": "Fraud", "value": 71205},
                    {"name": "Burglary", "value": 66442},
                ],
            }
        }
    )


class StateCrimeAnalyticsResponse(BaseModel):
    """Analytics for one crime category within a single state."""

    state: str
    crime_type: str
    total_cases: int
    total_arrests: int
    avg_charge_sheet_filed_pct: float | None
    avg_crime_rate_per_100k: float | None
    avg_police_response_time_min: float | None
    growth_pct_latest_year: float | None
    yearly_trend: list[YearValuePoint]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "state": "Rajasthan",
                "crime_type": "Murder",
                "total_cases": 92110,
                "total_arrests": 43124,
                "avg_charge_sheet_filed_pct": 71.23,
                "avg_crime_rate_per_100k": 3.42,
                "avg_police_response_time_min": 56.8,
                "growth_pct_latest_year": 4.15,
                "yearly_trend": [
                    {"year": 2023, "value": 3511},
                    {"year": 2024, "value": 3650},
                    {"year": 2025, "value": 3801},
                ],
            }
        }
    )


class NationalAnalyticsResponse(BaseModel):
    """India-wide crime analytics summary."""

    total_cases: int
    total_arrests: int
    avg_charge_sheet_filed_pct: float | None
    avg_crime_rate_per_100k: float | None
    avg_police_response_time_min: float | None
    top_dangerous_states: list[NamedMetric]
    top_crime_categories: list[NamedMetric]
    yearly_trend: list[YearValuePoint]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_cases": 12450231,
                "total_arrests": 5910230,
                "avg_charge_sheet_filed_pct": 68.91,
                "avg_crime_rate_per_100k": 10.74,
                "avg_police_response_time_min": 51.42,
                "top_dangerous_states": [
                    {"name": "Uttar Pradesh", "value": 1850340},
                    {"name": "Maharashtra", "value": 1622201},
                    {"name": "Rajasthan", "value": 1440321},
                ],
                "top_crime_categories": [
                    {"name": "Fraud", "value": 2045100},
                    {"name": "Assault", "value": 1822000},
                    {"name": "Murder", "value": 1634100},
                ],
                "yearly_trend": [
                    {"year": 2023, "value": 481204},
                    {"year": 2024, "value": 496820},
                    {"year": 2025, "value": 505112},
                ],
            }
        }
    )


class PredictionRequest(BaseModel):
    """Future-facing ML prediction input contract."""

    state: str = Field(..., example="Rajasthan")
    crime_type: str = Field(..., example="Murder")
    year: int = Field(..., ge=2000, example=2026)
    month: int | None = Field(default=None, ge=1, le=12, example=1)


class PredictionResponse(BaseModel):
    """Placeholder response until a trained model is integrated."""

    status: str
    message: str
    requested_input: PredictionRequest
    prediction: float | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "not_ready",
                "message": "Prediction model is not loaded yet. Connect a trained joblib artifact to enable forecasts.",
                "requested_input": {
                    "state": "Rajasthan",
                    "crime_type": "Murder",
                    "year": 2026,
                    "month": 1,
                },
                "prediction": None,
            }
        }
    )
