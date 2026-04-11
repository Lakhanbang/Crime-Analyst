"""CSV loader responsible for discovering, cleaning, and caching dataset state."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from app.config import get_settings
from app.utils.helpers import clean_column_name, normalize_lookup

logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = {
    "year",
    "state",
    "crime_type",
    "month",
    "number_of_cases",
    "arrests_made",
    "charge_sheet_filed_pct",
    "crime_rate_per_100k",
    "urban_or_rural",
    "victim_age_group",
    "victim_gender",
    "socioeconomic_factor",
    "police_response_time_min",
}

NUMERIC_COLUMNS = [
    "year",
    "month",
    "number_of_cases",
    "arrests_made",
    "charge_sheet_filed_pct",
    "crime_rate_per_100k",
    "police_response_time_min",
]


@dataclass(slots=True)
class DatasetCache:
    """In-memory dataset cache shared across routes and services."""

    dataframe: pd.DataFrame | None = None
    csv_path: Path | None = None


_CACHE = DatasetCache()


def _discover_csv_file() -> Path:
    """Find the configured CSV file or fall back to the first CSV in Database."""

    settings = get_settings()
    preferred = settings.preferred_csv_path
    if preferred.exists():
        return preferred

    csv_candidates = sorted(settings.database_dir.glob("*.csv"))
    if csv_candidates:
        logger.warning(
            "Configured CSV file was not found. Falling back to discovered CSV: %s",
            csv_candidates[0],
        )
        return csv_candidates[0]

    raise FileNotFoundError(
        f"No CSV file found in Database directory: {settings.database_dir}"
    )


def _prepare_dataframe(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Normalize columns, data types, and lookup keys for the analytics layer."""

    df = raw_df.copy()
    df.columns = [clean_column_name(column) for column in df.columns]

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(
            "Dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["state"] = df["state"].astype(str).str.strip()
    df["crime_type"] = df["crime_type"].astype(str).str.strip()
    df["state_key"] = df["state"].map(normalize_lookup)
    df["crime_type_key"] = df["crime_type"].map(normalize_lookup)

    string_columns = [
        "urban_or_rural",
        "victim_age_group",
        "victim_gender",
        "socioeconomic_factor",
    ]
    for column in string_columns:
        df[column] = df[column].fillna("Unknown").astype(str).str.strip()

    df = df.dropna(subset=["year", "number_of_cases"])
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].fillna(0).astype(int)

    logger.info("Prepared dataset with %s rows and %s columns", len(df), len(df.columns))
    return df


def load_crime_dataset() -> pd.DataFrame:
    """Load and cache the crime dataset if it has not been loaded already."""

    if _CACHE.dataframe is not None:
        return _CACHE.dataframe

    csv_path = _discover_csv_file()
    logger.info("Loading crime dataset from %s", csv_path)

    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    prepared_df = _prepare_dataframe(df)

    _CACHE.dataframe = prepared_df
    _CACHE.csv_path = csv_path
    return prepared_df


def get_crime_dataset() -> pd.DataFrame:
    """Return the cached dataset, loading it on first access if required."""

    return load_crime_dataset()


def get_dataset_metadata() -> dict[str, object]:
    """Expose lightweight metadata for health and diagnostics endpoints."""

    df = get_crime_dataset()
    return {
        "rows": int(len(df)),
        "columns": sorted(column for column in df.columns if not column.endswith("_key")),
        "year_range": {
            "start": int(df["year"].min()),
            "end": int(df["year"].max()),
        },
        "states_count": int(df["state"].nunique()),
        "crime_types_count": int(df["crime_type"].nunique()),
        "csv_file": str(_CACHE.csv_path) if _CACHE.csv_path else None,
    }
