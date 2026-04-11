"""Evaluation helpers for model scoring and reporting."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from utils import compute_mape


def calculate_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Compute the core regression metrics for one prediction run."""

    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "r2": float(r2_score(y_true, y_pred)),
        "mape": float(compute_mape(y_true, y_pred)),
    }


def build_leaderboard(metrics_rows: list[dict[str, object]]) -> pd.DataFrame:
    """Aggregate walk-forward metrics into a model leaderboard."""

    metrics_df = pd.DataFrame(metrics_rows)
    leaderboard = (
        metrics_df.groupby("model", as_index=False)[["mae", "rmse", "r2", "mape"]]
        .mean()
        .sort_values(["rmse", "mae", "mape"], ascending=[True, True, True])
        .reset_index(drop=True)
    )
    leaderboard["rank"] = leaderboard.index + 1
    return leaderboard[["rank", "model", "mae", "rmse", "r2", "mape"]]


def save_feature_importance(feature_names: list[str], importances: np.ndarray, output_path: Path) -> pd.DataFrame:
    """Save model feature importance values to CSV."""

    importance_df = (
        pd.DataFrame({"feature": feature_names, "importance": importances})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    importance_df.to_csv(output_path, index=False, encoding="utf-8")
    return importance_df
