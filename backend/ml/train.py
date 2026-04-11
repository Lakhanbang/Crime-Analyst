"""End-to-end training pipeline for crime forecasting models."""

from __future__ import annotations

import joblib
import pandas as pd
from catboost import CatBoostRegressor
from lightgbm import LGBMRegressor
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

from config import get_settings
from evaluate import build_leaderboard, calculate_metrics, save_feature_importance
from features import build_future_frame, create_training_features, get_feature_columns
from preprocess import aggregate_yearly, load_dataset
from utils import ensure_directories, save_dataframe, setup_logging


def build_model_registry(random_state: int) -> dict[str, object]:
    """Instantiate the forecasting models used in the leaderboard."""

    return {
        "xgboost_regressor": XGBRegressor(
            n_estimators=350,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=random_state,
            n_jobs=-1,
        ),
        "lightgbm_regressor": LGBMRegressor(
            n_estimators=400,
            learning_rate=0.05,
            num_leaves=31,
            subsample=0.9,
            colsample_bytree=0.9,
            random_state=random_state,
        ),
        "catboost_regressor": CatBoostRegressor(
            iterations=400,
            depth=8,
            learning_rate=0.05,
            loss_function="RMSE",
            random_seed=random_state,
            verbose=False,
        ),
        "random_forest_regressor": RandomForestRegressor(
            n_estimators=400,
            max_depth=18,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
        "extra_trees_regressor": ExtraTreesRegressor(
            n_estimators=500,
            max_depth=20,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1,
        ),
    }


def build_preprocessor(numeric_columns: list[str], categorical_columns: list[str]) -> ColumnTransformer:
    """Create a reusable preprocessing transformer for numeric and categorical inputs."""

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, numeric_columns),
            ("categorical", categorical_pipeline, categorical_columns),
        ],
        remainder="drop",
    )


def walk_forward_validate(
    feature_df: pd.DataFrame,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    validation_years: list[int],
    random_state: int,
    logger,
) -> tuple[pd.DataFrame, list[dict[str, object]]]:
    """Run time-aware validation across the requested yearly folds."""

    model_registry = build_model_registry(random_state)
    metrics_rows: list[dict[str, object]] = []

    for test_year in validation_years:
        train_df = feature_df[feature_df["year"] < test_year].copy()
        test_df = feature_df[feature_df["year"] == test_year].copy()

        if train_df.empty or test_df.empty:
            logger.warning("Skipping validation year %s due to empty train/test split", test_year)
            continue

        X_train = train_df[feature_columns]
        y_train = train_df["cases_reported"].astype(float)
        X_test = test_df[feature_columns]
        y_test = test_df["cases_reported"].astype(float)

        for model_name, model in model_registry.items():
            preprocessor = build_preprocessor(numeric_columns, categorical_columns)
            transformed_train = preprocessor.fit_transform(X_train)
            transformed_test = preprocessor.transform(X_test)

            model.fit(transformed_train, y_train)
            predictions = model.predict(transformed_test)
            metrics = calculate_metrics(y_test.to_numpy(), predictions)
            metrics_rows.append({"model": model_name, "test_year": test_year, **metrics})
            logger.info("Validated %s on %s with RMSE %.4f", model_name, test_year, metrics["rmse"])

    leaderboard = build_leaderboard(metrics_rows)
    return leaderboard, metrics_rows


def train_final_models(
    feature_df: pd.DataFrame,
    feature_columns: list[str],
    numeric_columns: list[str],
    categorical_columns: list[str],
    base_history_df: pd.DataFrame,
    saved_models_dir,
    random_state: int,
    logger,
) -> dict[str, dict[str, object]]:
    """Train all models on the full dataset and persist their artifacts."""

    model_registry = build_model_registry(random_state)
    model_bundles: dict[str, dict[str, object]] = {}
    X_full = feature_df[feature_columns]
    y_full = feature_df["cases_reported"].astype(float)

    for model_name, model in model_registry.items():
        preprocessor = build_preprocessor(numeric_columns, categorical_columns)
        transformed_full = preprocessor.fit_transform(X_full)
        model.fit(transformed_full, y_full)

        bundle = {
            "model_name": model_name,
            "model": model,
            "preprocessor": preprocessor,
            "feature_columns": feature_columns,
            "numeric_columns": numeric_columns,
            "categorical_columns": categorical_columns,
            "history_df": base_history_df.copy(),
            "train_year_min": int(base_history_df["year"].min()),
            "train_year_max": int(base_history_df["year"].max()),
        }
        model_bundles[model_name] = bundle
        output_path = saved_models_dir / f"{model_name}.pkl"
        joblib.dump(bundle, output_path)
        logger.info("Saved trained model bundle to %s", output_path)

    return model_bundles


def get_transformed_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """Resolve feature names after one-hot encoding for reporting."""

    return list(preprocessor.get_feature_names_out())


def generate_future_predictions(best_bundle: dict[str, object], years: list[int]) -> pd.DataFrame:
    """Forecast future yearly crime totals recursively for all state-crime pairs."""

    history_df = best_bundle["history_df"].copy()
    model = best_bundle["model"]
    preprocessor = best_bundle["preprocessor"]
    feature_columns = best_bundle["feature_columns"]

    all_predictions: list[pd.DataFrame] = []
    for year in years:
        future_base = build_future_frame(history_df, year)
        combined_df = pd.concat([history_df, future_base], ignore_index=True)
        engineered_df = create_training_features(combined_df)
        future_features = engineered_df[engineered_df["year"] == year].copy()

        transformed = preprocessor.transform(future_features[feature_columns])
        future_base["predicted_cases"] = model.predict(transformed)
        future_base["cases_reported"] = future_base["predicted_cases"]
        all_predictions.append(
            future_base[
                [
                    "year",
                    "state",
                    "crime_type",
                    "predicted_cases",
                    "arrests",
                    "charge_sheet_rate",
                    "crime_rate",
                    "police_response_time",
                ]
            ].copy()
        )
        history_df = pd.concat([history_df, future_base.drop(columns=["predicted_cases"])], ignore_index=True)

    return pd.concat(all_predictions, ignore_index=True)


def main() -> None:
    """Train all forecasting models, save artifacts, and produce reports."""

    settings = get_settings()
    ensure_directories([settings.saved_models_dir, settings.reports_dir])
    logger = setup_logging()

    logger.info("Loading dataset from %s", settings.data_path)
    raw_df, metadata = load_dataset(settings)
    yearly_df = aggregate_yearly(raw_df, metadata)
    logger.info("Prepared yearly training frame with %s rows", len(yearly_df))

    feature_df = create_training_features(yearly_df)
    numeric_columns, categorical_columns = get_feature_columns(feature_df)
    feature_columns = numeric_columns + categorical_columns

    training_df = feature_df[feature_df["year"] >= (int(feature_df["year"].min()) + 1)].copy()
    training_df = training_df.sort_values(["year", "state", "crime_type"]).reset_index(drop=True)

    leaderboard, metrics_rows = walk_forward_validate(
        feature_df=training_df,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        validation_years=settings.validation_years,
        random_state=settings.random_state,
        logger=logger,
    )
    save_dataframe(leaderboard, settings.leaderboard_path)
    logger.info("Saved leaderboard report to %s", settings.leaderboard_path)

    model_bundles = train_final_models(
        feature_df=training_df,
        feature_columns=feature_columns,
        numeric_columns=numeric_columns,
        categorical_columns=categorical_columns,
        base_history_df=yearly_df,
        saved_models_dir=settings.saved_models_dir,
        random_state=settings.random_state,
        logger=logger,
    )

    best_model_name = str(leaderboard.iloc[0]["model"])
    best_bundle = model_bundles[best_model_name]
    joblib.dump(best_bundle, settings.best_model_path)
    logger.info("Saved best model bundle to %s", settings.best_model_path)

    transformed_feature_names = get_transformed_feature_names(best_bundle["preprocessor"])
    importances = getattr(best_bundle["model"], "feature_importances_", None)
    if importances is None:
        raise ValueError(f"Selected best model does not expose feature_importances_: {best_model_name}")
    save_feature_importance(transformed_feature_names, importances, settings.feature_importance_path)
    logger.info("Saved feature importance report to %s", settings.feature_importance_path)

    future_predictions = generate_future_predictions(best_bundle, settings.forecast_years)
    save_dataframe(future_predictions, settings.future_predictions_path)
    logger.info("Saved future predictions report to %s", settings.future_predictions_path)

    metrics_df = pd.DataFrame(metrics_rows)

    print("\nBest model:", best_model_name)
    print("\nAll metrics:")
    print(leaderboard.to_string(index=False))
    print("\nFiles saved:")
    print(f"- Leaderboard: {settings.leaderboard_path}")
    print(f"- Feature importance: {settings.feature_importance_path}")
    print(f"- Future predictions: {settings.future_predictions_path}")
    print(f"- Best model: {settings.best_model_path}")
    print(f"- All model artifacts: {settings.saved_models_dir}")
    print("\nValidation folds:")
    print(metrics_df.to_string(index=False))


if __name__ == "__main__":
    main()
