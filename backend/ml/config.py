"""Configuration for the crime forecasting training pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Settings:
    """Centralized runtime settings for dataset paths, outputs, and training."""

    root_dir: Path = Path(__file__).resolve().parents[2]
    data_path: Path = Path(__file__).resolve().parents[2] / "Database" / "India_Crime_Dataset_StateWise_2000_2025.csv"
    ml_dir: Path = Path(__file__).resolve().parent
    saved_models_dir: Path = Path(__file__).resolve().parent / "saved_models"
    reports_dir: Path = Path(__file__).resolve().parent / "reports"
    best_model_path: Path = Path(__file__).resolve().parent / "saved_models" / "best_model.pkl"
    leaderboard_path: Path = Path(__file__).resolve().parent / "reports" / "model_leaderboard.csv"
    feature_importance_path: Path = Path(__file__).resolve().parent / "reports" / "feature_importance.csv"
    future_predictions_path: Path = Path(__file__).resolve().parent / "reports" / "future_predictions_2026_2030.csv"
    forecast_years: list[int] = field(default_factory=lambda: [2026, 2027, 2028, 2029, 2030])
    validation_years: list[int] = field(default_factory=lambda: [2022, 2023, 2024, 2025])
    random_state: int = 42
    target_aliases: tuple[str, ...] = (
        "cases_reported",
        "case_reported",
        "number_of_cases",
        "reported_cases",
        "cases",
        "crime_cases",
        "total_cases",
    )
    year_aliases: tuple[str, ...] = ("year", "crime_year")
    state_aliases: tuple[str, ...] = ("state", "state_name", "region", "state_ut")
    crime_aliases: tuple[str, ...] = ("crime_type", "crime", "crime_category", "category")
    arrests_aliases: tuple[str, ...] = ("arrests_made", "arrests", "total_arrests")
    charge_sheet_aliases: tuple[str, ...] = (
        "charge_sheet_filed_pct",
        "charge_sheet_rate",
        "charge_sheet_percentage",
    )
    crime_rate_aliases: tuple[str, ...] = ("crime_rate_per_100k", "crime_rate", "rate_per_100k")
    police_response_aliases: tuple[str, ...] = (
        "police_response_time_min",
        "response_time",
        "police_response_time",
    )
    month_aliases: tuple[str, ...] = ("month", "crime_month")
    urban_aliases: tuple[str, ...] = ("urban_or_rural", "urban_rural", "area_type")
    victim_age_aliases: tuple[str, ...] = ("victim_age_group", "age_group")
    victim_gender_aliases: tuple[str, ...] = ("victim_gender", "gender")
    socioeconomic_aliases: tuple[str, ...] = ("socioeconomic_factor", "income_group", "economic_factor")
    clip_quantiles: tuple[float, float] = (0.01, 0.99)


def get_settings() -> Settings:
    """Return pipeline settings."""

    return Settings()
