"""Dataset loading, cleaning, and yearly aggregation for forecasting."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from config import Settings
from utils import clean_column_name, clip_series, detect_column, safe_mode


@dataclass(slots=True)
class DatasetMetadata:
    """Resolved dataset column mapping used downstream."""

    year_col: str
    state_col: str
    crime_col: str
    target_col: str
    arrests_col: str | None
    charge_sheet_col: str | None
    crime_rate_col: str | None
    police_response_col: str | None
    month_col: str | None
    urban_col: str | None
    victim_age_col: str | None
    victim_gender_col: str | None
    socioeconomic_col: str | None


def resolve_metadata(df: pd.DataFrame, settings: Settings) -> DatasetMetadata:
    """Inspect dataset columns and resolve the fields required by the pipeline."""

    columns = list(df.columns)
    return DatasetMetadata(
        year_col=detect_column(columns, settings.year_aliases),
        state_col=detect_column(columns, settings.state_aliases),
        crime_col=detect_column(columns, settings.crime_aliases),
        target_col=detect_column(columns, settings.target_aliases),
        arrests_col=detect_column(columns, settings.arrests_aliases, required=False),
        charge_sheet_col=detect_column(columns, settings.charge_sheet_aliases, required=False),
        crime_rate_col=detect_column(columns, settings.crime_rate_aliases, required=False),
        police_response_col=detect_column(columns, settings.police_response_aliases, required=False),
        month_col=detect_column(columns, settings.month_aliases, required=False),
        urban_col=detect_column(columns, settings.urban_aliases, required=False),
        victim_age_col=detect_column(columns, settings.victim_age_aliases, required=False),
        victim_gender_col=detect_column(columns, settings.victim_gender_aliases, required=False),
        socioeconomic_col=detect_column(columns, settings.socioeconomic_aliases, required=False),
    )


def load_dataset(settings: Settings) -> tuple[pd.DataFrame, DatasetMetadata]:
    """Load the raw CSV and clean its schema before aggregation."""

    if not settings.data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {settings.data_path}")

    raw_df = pd.read_csv(settings.data_path, encoding="utf-8-sig")
    raw_df.columns = [clean_column_name(column) for column in raw_df.columns]
    raw_df = raw_df.drop_duplicates().copy()

    metadata = resolve_metadata(raw_df, settings)
    cleaned_df = _clean_dataset(raw_df, metadata, settings)
    return cleaned_df, metadata


def _clean_dataset(df: pd.DataFrame, metadata: DatasetMetadata, settings: Settings) -> pd.DataFrame:
    """Normalize dtypes, handle missing values, and clip outliers."""

    working_df = df.copy()

    required_numeric = [metadata.year_col, metadata.target_col]
    optional_numeric = [
        metadata.arrests_col,
        metadata.charge_sheet_col,
        metadata.crime_rate_col,
        metadata.police_response_col,
        metadata.month_col,
    ]
    for column in required_numeric + [col for col in optional_numeric if col]:
        working_df[column] = pd.to_numeric(working_df[column], errors="coerce")

    for column in [metadata.state_col, metadata.crime_col]:
        working_df[column] = working_df[column].fillna("Unknown").astype(str).str.strip()

    optional_categoricals = [
        metadata.urban_col,
        metadata.victim_age_col,
        metadata.victim_gender_col,
        metadata.socioeconomic_col,
    ]
    for column in [col for col in optional_categoricals if col]:
        working_df[column] = working_df[column].fillna("Unknown").astype(str).str.strip()

    working_df = working_df.dropna(subset=[metadata.year_col, metadata.target_col]).copy()
    working_df[metadata.year_col] = working_df[metadata.year_col].astype(int)

    for column in [metadata.target_col, metadata.arrests_col, metadata.crime_rate_col, metadata.police_response_col]:
        if column:
            working_df[column] = clip_series(
                working_df[column],
                lower_q=settings.clip_quantiles[0],
                upper_q=settings.clip_quantiles[1],
            )

    return working_df


def aggregate_yearly(df: pd.DataFrame, metadata: DatasetMetadata) -> pd.DataFrame:
    """Aggregate monthly rows into yearly state-crime forecasting records."""

    group_cols = [metadata.year_col, metadata.state_col, metadata.crime_col]
    aggregation_map: dict[str, str] = {
        metadata.target_col: "sum",
    }

    if metadata.arrests_col:
        aggregation_map[metadata.arrests_col] = "sum"
    if metadata.charge_sheet_col:
        aggregation_map[metadata.charge_sheet_col] = "mean"
    if metadata.crime_rate_col:
        aggregation_map[metadata.crime_rate_col] = "mean"
    if metadata.police_response_col:
        aggregation_map[metadata.police_response_col] = "mean"
    if metadata.month_col:
        aggregation_map[metadata.month_col] = "nunique"

    aggregated = df.groupby(group_cols, as_index=False).agg(aggregation_map)

    if metadata.urban_col:
        urban_mode = (
            df.groupby(group_cols)[metadata.urban_col]
            .apply(safe_mode)
            .reset_index(name="dominant_urban_or_rural")
        )
        aggregated = aggregated.merge(urban_mode, on=group_cols, how="left")
    else:
        aggregated["dominant_urban_or_rural"] = "Unknown"

    if metadata.victim_age_col:
        age_mode = (
            df.groupby(group_cols)[metadata.victim_age_col]
            .apply(safe_mode)
            .reset_index(name="dominant_victim_age_group")
        )
        aggregated = aggregated.merge(age_mode, on=group_cols, how="left")
    else:
        aggregated["dominant_victim_age_group"] = "Unknown"

    if metadata.victim_gender_col:
        gender_mode = (
            df.groupby(group_cols)[metadata.victim_gender_col]
            .apply(safe_mode)
            .reset_index(name="dominant_victim_gender")
        )
        aggregated = aggregated.merge(gender_mode, on=group_cols, how="left")
    else:
        aggregated["dominant_victim_gender"] = "Unknown"

    if metadata.socioeconomic_col:
        socioeconomic_mode = (
            df.groupby(group_cols)[metadata.socioeconomic_col]
            .apply(safe_mode)
            .reset_index(name="dominant_socioeconomic_factor")
        )
        aggregated = aggregated.merge(socioeconomic_mode, on=group_cols, how="left")
    else:
        aggregated["dominant_socioeconomic_factor"] = "Unknown"

    rename_map = {
        metadata.year_col: "year",
        metadata.state_col: "state",
        metadata.crime_col: "crime_type",
        metadata.target_col: "cases_reported",
    }
    if metadata.arrests_col:
        rename_map[metadata.arrests_col] = "arrests"
    if metadata.charge_sheet_col:
        rename_map[metadata.charge_sheet_col] = "charge_sheet_rate"
    if metadata.crime_rate_col:
        rename_map[metadata.crime_rate_col] = "crime_rate"
    if metadata.police_response_col:
        rename_map[metadata.police_response_col] = "police_response_time"
    if metadata.month_col:
        rename_map[metadata.month_col] = "observed_months"

    aggregated = aggregated.rename(columns=rename_map)

    for column, default_value in {
        "arrests": 0.0,
        "charge_sheet_rate": 0.0,
        "crime_rate": 0.0,
        "police_response_time": 0.0,
        "observed_months": 12.0,
    }.items():
        if column not in aggregated.columns:
            aggregated[column] = default_value

    aggregated["arrests_per_case"] = (
        aggregated["arrests"] / aggregated["cases_reported"].replace(0, pd.NA)
    ).fillna(0.0)
    aggregated["year"] = aggregated["year"].astype(int)
    aggregated = aggregated.sort_values(["state", "crime_type", "year"]).reset_index(drop=True)
    return aggregated
