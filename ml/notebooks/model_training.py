import pandas as pd
import numpy as np
import joblib
import lightgbm as lgbm
from pathlib import Path
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from typing import Tuple, Dict, List

POLLUTANTS = ["pm2_5", "pm10", "no2", "o3", "so2", "european_aqi"]
HORIZONS = ["4h", "8h", "12h"]
SPLIT_DATE = "2025-2-20"
NON_FEATURE_COLS = ["timestamp", "borough"]

def load_features() -> pd.DataFrame:
    """Load engineered features parquet"""

    return pd.read_parquet("data/processed/all_boroughs_features.parquet")

def get_feature_columns(df: pd.DataFrame) -> List:
    """Get feature columns by dropping targets and non features"""

    feature_columns = []
    for col in df.columns:
        if not col.startswith("target") and col not in NON_FEATURE_COLS:
            feature_columns.append(col)
        
    return feature_columns

def train_test_split(df: pd.DataFrame, target: str) -> Tuple:
    """Split into train and test sets by date"""

    feature_cols = get_feature_columns(df)
    X = df[feature_cols]
    y = df[target]
    
    mask = df["timestamp"] < SPLIT_DATE
    return X[mask], X[~mask], y[mask], y[~mask]

def train_model(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> lgbm.LGBMRegressor:
    """Train a single LGBM model"""

    model = lgbm.LGBMRegressor(
        n_estimators=1000,
        learning_rate=0.05,
        num_leaves=31,
        random_state=40,
        early_stopping_rounds=50
    )

    model.fit(X_train,y_train, eval_set=[(X_test, y_test)])

    return model

def evaluate_model(model: lgbm.LGBMRegressor, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
    """Evaluate model performance and return metrics"""

    predictions = model.predict(X_test)

    return {
        "mae": mean_absolute_error(y_test, predictions),
       "rmse": root_mean_squared_error(y_test, predictions),
       "r2": r2_score(y_test, predictions)
    }

def save_model(model: lgbm.LGBMRegressor, pollutant: str, horizon: str):
    """Save model to models folder"""

    path = Path(f"models/{pollutant}")
    path.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path / f"{pollutant}_{horizon}.pkl")

def train_all_models(df: pd.DataFrame) -> Dict:
    """Train all 12 LGBM models"""

    all_metrics = {}

    for pollutant in POLLUTANTS:
        for horizon in HORIZONS:
            target = f"target_{pollutant}_{horizon}"

            X_train, X_test, y_train, y_test = train_test_split(df, target)
            model = train_model(X_train, y_train, X_test, y_test)
            metrics= evaluate_model(model, X_test, y_test)
            save_model(model, pollutant, horizon)

            all_metrics[f"{pollutant}_{horizon}"] = metrics
            print(f"{pollutant} {horizon} - MAE: {metrics['mae']:.2f}, RMSE: {metrics['rmse']:.2f}, R2: {metrics['r2']:.3f}")

    return all_metrics

if __name__ == "__main__":
    df = load_features()
    train_all_models(df)