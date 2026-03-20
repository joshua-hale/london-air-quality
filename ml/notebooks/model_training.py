# train.py

import pandas as pd
import numpy as np
import joblib
import lightgbm as lgbm
import boto3
from pathlib import Path
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from typing import Tuple, Dict, List

from feature_engineering import build_features_for_training, get_feature_columns

POLLUTANTS = ["pm2_5", "pm10", "no2", "o3", "so2", "european_aqi"]
HORIZONS = ["4h", "8h"]
SPLIT_DATE = "2025-02-20"
NON_FEATURE_COLS = ["timestamp", "borough"]
S3_BUCKET = "london-air-quality-data-dev"

def load_and_prepare_data() -> Tuple[pd.DataFrame, Dict]:
    """Load cleaned data, run feature engineering, return features and borough_map"""

    df = pd.read_parquet("data/processed/cleaned_data.parquet")
    df = df.sort_values(["borough", "timestamp"]).reset_index(drop=True)
    df, borough_map = build_features_for_training(df)
    return df, borough_map

def train_test_split(df: pd.DataFrame, target: str, feature_cols: List[str]) -> Tuple:
    """Split into train and test sets by date"""

    X = df[feature_cols]
    y = df[target]

    mask = df["timestamp"] < SPLIT_DATE
    return X[mask], X[~mask], y[mask], y[~mask]

def train_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> lgbm.LGBMRegressor:
    """Train a single LGBMRegressor with early stopping"""

    model = lgbm.LGBMRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        num_leaves=31,
        random_state=40,
        early_stopping_rounds=50
    )

    model.fit(X_train, y_train, eval_set=[(X_test, y_test)])
    return model

def evaluate_model(
    model: lgbm.LGBMRegressor,
    X_test: pd.DataFrame,
    y_test: pd.Series
) -> Dict:
    """Evaluate model and return MAE, RMSE, R2"""

    predictions = model.predict(X_test)
    return {
        "mae": mean_absolute_error(y_test, predictions),
        "rmse": root_mean_squared_error(y_test, predictions),
        "r2": r2_score(y_test, predictions)
    }

def save_model_locally(model: lgbm.LGBMRegressor, pollutant: str, horizon: str):
    """Save model artifact to local models directory"""

    path = Path(f"models/{pollutant}")
    path.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path / f"{pollutant}_{horizon}.pkl")

def save_artifacts_locally(borough_map: Dict, feature_cols: List[str]):
    """Save borough_map and feature_columns artifacts locally"""

    Path("models").mkdir(exist_ok=True)
    joblib.dump(borough_map, "models/borough_map.pkl")
    joblib.dump(feature_cols, "models/feature_columns.pkl")
    print(f"Saved borough_map ({len(borough_map)} boroughs) and {len(feature_cols)} feature columns")

def upload_models_to_s3(bucket: str):
    """Upload all model artifacts to S3 after training completes"""

    s3 = boto3.client("s3")
    for path in Path("models").rglob("*.pkl"):
        key = f"models/{path.relative_to('models')}"
        s3.upload_file(str(path), bucket, key)
        print(f"Uploaded s3://{bucket}/{key}")

def upload_models_to_minio(bucket: str):
    """Upload model artifacts to local MinIO instance for development."""

    s3 = boto3.client(
        "s3",
        endpoint_url="http://localhost:9000",
        aws_access_key_id="minioadmin",
        aws_secret_access_key="minioadmin"
    )

    for path in Path("models").rglob("*.pkl"):
        key = f"models/{path.relative_to('models')}"
        s3.upload_file(str(path), bucket, key)
        print(f"Uploaded to MinIO: {key}")


def train_all_models(df: pd.DataFrame, feature_cols: List[str]) -> Dict:
    """Train all 18 LGBMRegressors (6 pollutants x 3 horizons)"""

    all_metrics = {}

    for pollutant in POLLUTANTS:
        for horizon in HORIZONS:
            target = f"target_{pollutant}_{horizon}"

            X_train, X_test, y_train, y_test = train_test_split(df, target, feature_cols)
            model = train_model(X_train, y_train, X_test, y_test)
            metrics = evaluate_model(model, X_test, y_test)
            save_model_locally(model, pollutant, horizon)

            all_metrics[f"{pollutant}_{horizon}"] = metrics
            print(f"{pollutant} {horizon} — MAE: {metrics['mae']:.2f}, RMSE: {metrics['rmse']:.2f}, R2: {metrics['r2']:.3f}")

    return all_metrics

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", help="Upload to MinIO instead of real S3")
    args = parser.parse_args()

    df, borough_map = load_and_prepare_data()
    feature_cols = get_feature_columns(df)
    save_artifacts_locally(borough_map, feature_cols)
    metrics = train_all_models(df, feature_cols)

    if args.local:
        upload_models_to_minio("london-air-data")
        print("Uploaded to MinIO for local dev")
    else:
        upload_models_to_s3(S3_BUCKET)
        print(f"Uploaded to real S3: {S3_BUCKET}")

    print("\nAll models trained and uploaded.")
    print("\nFinal metrics:")
    for model_name, m in metrics.items():
        print(f"  {model_name}: MAE={m['mae']:.2f}, RMSE={m['rmse']:.2f}, R2={m['r2']:.3f}")