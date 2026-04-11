"""Reusable helper utilities for normalization and safe calculations."""

from __future__ import annotations

import re
from typing import Iterable


def clean_column_name(value: str) -> str:
    """Convert raw CSV headers into normalized snake_case column names."""

    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", normalized).strip("_")


def normalize_lookup(value: str) -> str:
    """Normalize user-provided state and crime names for case-insensitive matching."""

    return re.sub(r"\s+", " ", value.strip().casefold())


def safe_percentage_change(previous: float, current: float) -> float | None:
    """Return percentage growth while avoiding division-by-zero errors."""

    if previous == 0:
        return None
    return round(((current - previous) / previous) * 100, 2)


def to_float(value: float | int | None) -> float | None:
    """Convert numeric values to rounded floats for clean JSON output."""

    if value is None:
        return None
    return round(float(value), 2)


def title_sorted(values: Iterable[str]) -> list[str]:
    """Sort strings case-insensitively while preserving original text."""

    return sorted(values, key=lambda item: item.casefold())
