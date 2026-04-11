"""Utility helpers shared across the ML pipeline."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


def setup_logging() -> logging.Logger:
    """Configure module-level logging and return the main pipeline logger."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    return logging.getLogger("crime_ml_pipeline")


def ensure_directories(paths: Iterable[Path]) -> None:
    """Create required directories if they do not already exist."""

    for path in paths:
        path.mkdir(parents=True, exist_ok=True)


def clean_column_name(value: str) -> str:
    """Normalize raw dataset columns to snake_case."""

    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", normalized).strip("_")


def normalize_text(value: str) -> str:
    """Normalize free text for resilient matching."""

    return re.sub(r"\s+", " ", value.strip().lower())


def detect_column(columns: list[str], aliases: Iterable[str], required: bool = True) -> str | None:
    """Detect the best matching dataset column from a list of aliases."""

    cleaned_columns = {clean_column_name(column): column for column in columns}
    normalized_candidates = {normalize_text(key): value for key, value in cleaned_columns.items()}

    for alias in aliases:
        alias_clean = clean_column_name(alias)
        if alias_clean in cleaned_columns:
            return cleaned_columns[alias_clean]
        alias_normalized = normalize_text(alias_clean)
        if alias_normalized in normalized_candidates:
            return normalized_candidates[alias_normalized]

    if not required:
        return None
    raise ValueError(f"Unable to detect required column from aliases: {list(aliases)}")


def safe_mode(series: pd.Series) -> str:
    """Return the most frequent non-null categorical value."""

    cleaned = series.dropna().astype(str).str.strip()
    if cleaned.empty:
        return "Unknown"
    mode_values = cleaned.mode()
    if mode_values.empty:
        return "Unknown"
    return str(mode_values.iloc[0])


def clip_series(series: pd.Series, lower_q: float, upper_q: float) -> pd.Series:
    """Clip a numeric series using quantile-based bounds."""

    if series.dropna().empty:
        return series
    lower_bound = series.quantile(lower_q)
    upper_bound = series.quantile(upper_q)
    return series.clip(lower=lower_bound, upper=upper_bound)


def save_dataframe(df: pd.DataFrame, path: Path) -> None:
    """Persist a DataFrame to CSV with UTF-8 encoding."""

    df.to_csv(path, index=False, encoding="utf-8")


def compute_mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    """Calculate mean absolute percentage error safely."""

    denominator = np.where(np.abs(y_true) < 1e-8, 1.0, np.abs(y_true))
    return float(np.mean(np.abs((y_true - y_pred) / denominator)) * 100.0)
