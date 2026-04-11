"""Feature engineering for yearly crime forecasting."""

from __future__ import annotations

import numpy as np
import pandas as pd


GROUP_KEYS = ["state", "crime_type"]
NUMERIC_HISTORY_COLUMNS = [
    "arrests",
    "charge_sheet_rate",
    "crime_rate",
    "police_response_time",
    "observed_months",
    "arrests_per_case",
]
CATEGORICAL_HISTORY_COLUMNS = [
    "dominant_urban_or_rural",
    "dominant_victim_age_group",
    "dominant_victim_gender",
    "dominant_socioeconomic_factor",
]


def create_training_features(base_df: pd.DataFrame) -> pd.DataFrame:
    """Create leakage-safe forecasting features from yearly aggregated records."""

    df = base_df.copy().sort_values(GROUP_KEYS + ["year"]).reset_index(drop=True)
    grouped = df.groupby(GROUP_KEYS, group_keys=False)

    df["lag_1"] = grouped["cases_reported"].shift(1)
    df["lag_2"] = grouped["cases_reported"].shift(2)
    df["rolling_mean_3"] = grouped["cases_reported"].transform(
        lambda series: series.shift(1).rolling(window=3, min_periods=1).mean()
    )
    df["rolling_std_3"] = grouped["cases_reported"].transform(
        lambda series: series.shift(1).rolling(window=3, min_periods=2).std()
    )
    df["yearly_growth_rate"] = ((df["lag_1"] - df["lag_2"]) / df["lag_2"].replace(0, np.nan)) * 100.0

    state_year_totals = (
        df.groupby(["state", "year"], as_index=False)["cases_reported"]
        .sum()
        .sort_values(["state", "year"])
    )
    state_year_totals["state_historical_average"] = (
        state_year_totals.groupby("state")["cases_reported"]
        .transform(lambda series: series.shift(1).expanding().mean())
    )
    df = df.merge(
        state_year_totals[["state", "year", "state_historical_average"]],
        on=["state", "year"],
        how="left",
    )

    crime_year_totals = (
        df.groupby(["crime_type", "year"], as_index=False)["cases_reported"]
        .sum()
        .sort_values(["crime_type", "year"])
    )
    crime_year_totals["crime_historical_average"] = (
        crime_year_totals.groupby("crime_type")["cases_reported"]
        .transform(lambda series: series.shift(1).expanding().mean())
    )
    df = df.merge(
        crime_year_totals[["crime_type", "year", "crime_historical_average"]],
        on=["crime_type", "year"],
        how="left",
    )

    df["state_crime_interaction_trend"] = (
        grouped["cases_reported"]
        .transform(lambda series: series.shift(1).expanding().mean())
    )
    df["year_numeric_trend"] = df["year"] - int(df["year"].min())

    for column in NUMERIC_HISTORY_COLUMNS:
        df[f"{column}_lag_1"] = grouped[column].shift(1)
        df[f"{column}_rolling_mean_3"] = grouped[column].transform(
            lambda series: series.shift(1).rolling(window=3, min_periods=1).mean()
        )

    for column in CATEGORICAL_HISTORY_COLUMNS:
        df[f"{column}_prev"] = grouped[column].shift(1).fillna("Unknown")

    df["state_crime_key"] = df["state"] + " | " + df["crime_type"]
    df = df.replace([np.inf, -np.inf], np.nan)
    return df


def get_feature_columns(feature_df: pd.DataFrame) -> tuple[list[str], list[str]]:
    """Return the numeric and categorical feature columns used for training."""

    numeric_columns = [
        "year",
        "year_numeric_trend",
        "lag_1",
        "lag_2",
        "rolling_mean_3",
        "rolling_std_3",
        "yearly_growth_rate",
        "state_historical_average",
        "crime_historical_average",
        "state_crime_interaction_trend",
        "arrests_lag_1",
        "arrests_rolling_mean_3",
        "charge_sheet_rate_lag_1",
        "charge_sheet_rate_rolling_mean_3",
        "crime_rate_lag_1",
        "crime_rate_rolling_mean_3",
        "police_response_time_lag_1",
        "police_response_time_rolling_mean_3",
        "observed_months_lag_1",
        "observed_months_rolling_mean_3",
        "arrests_per_case_lag_1",
        "arrests_per_case_rolling_mean_3",
    ]
    numeric_columns = [column for column in numeric_columns if column in feature_df.columns]

    categorical_columns = [
        "state",
        "crime_type",
        "state_crime_key",
        "dominant_urban_or_rural_prev",
        "dominant_victim_age_group_prev",
        "dominant_victim_gender_prev",
        "dominant_socioeconomic_factor_prev",
    ]
    categorical_columns = [column for column in categorical_columns if column in feature_df.columns]
    return numeric_columns, categorical_columns


def build_future_frame(history_df: pd.DataFrame, target_year: int) -> pd.DataFrame:
    """Create future-year skeleton rows using the latest available group history."""

    records: list[dict[str, object]] = []
    for _, group in history_df.groupby(GROUP_KEYS):
        ordered = group.sort_values("year")
        last_row = ordered.iloc[-1]
        numeric_means = ordered[NUMERIC_HISTORY_COLUMNS].mean(numeric_only=True)

        records.append(
            {
                "year": target_year,
                "state": last_row["state"],
                "crime_type": last_row["crime_type"],
                "cases_reported": np.nan,
                "arrests": float(numeric_means.get("arrests", last_row.get("arrests", 0.0))),
                "charge_sheet_rate": float(
                    numeric_means.get("charge_sheet_rate", last_row.get("charge_sheet_rate", 0.0))
                ),
                "crime_rate": float(numeric_means.get("crime_rate", last_row.get("crime_rate", 0.0))),
                "police_response_time": float(
                    numeric_means.get("police_response_time", last_row.get("police_response_time", 0.0))
                ),
                "observed_months": float(last_row.get("observed_months", 12.0)),
                "arrests_per_case": float(
                    numeric_means.get("arrests_per_case", last_row.get("arrests_per_case", 0.0))
                ),
                "dominant_urban_or_rural": last_row.get("dominant_urban_or_rural", "Unknown"),
                "dominant_victim_age_group": last_row.get("dominant_victim_age_group", "Unknown"),
                "dominant_victim_gender": last_row.get("dominant_victim_gender", "Unknown"),
                "dominant_socioeconomic_factor": last_row.get(
                    "dominant_socioeconomic_factor",
                    "Unknown",
                ),
            }
        )

    return pd.DataFrame.from_records(records)
