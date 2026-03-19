# feature_engineering.py

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple

POLLUTANTS = ["pm2_5", "pm10", "no2", "o3", "so2", "european_aqi"]
NON_FEATURE_COLS = ["timestamp", "borough"]

def build_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build all temporal features required for predictions"""

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_of_week
    df["month"] = df["timestamp"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5,6]).astype(int)
    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)

    return df

def build_lag_features(variables: List[str], df: pd.DataFrame) -> pd.DataFrame:
    """Build all lag features required for predictions"""

    lag_times = [1, 2, 3, 4, 5, 6, 8, 10, 12, 24, 36, 48]

    for variable in variables:
        for lag in lag_times:
            df[f"{variable}_lag_{lag}h"] = df.groupby("borough")[variable].shift(lag)

    return df

def build_rolling_features(variables: List[str], df: pd.DataFrame) -> pd.DataFrame:
    """Build all rolling features required for predictions"""

    windows = [3, 6, 9, 12, 24, 48]

    for variable in variables:
        for window in windows:
            df[f"{variable}_rolling_{window}h"] = (
                df.groupby("borough")[variable]
                .transform(lambda x: x.rolling(window).mean()))

    return df

def build_wind_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build all wind features required for predictions"""

    df["wind_direction_sin"] = np.sin(np.radians(df["wind_direction_10m"]))
    df["wind_direction_cos"] = np.cos(np.radians(df["wind_direction_10m"]))

    return df

def build_borough_encodings(df: pd.DataFrame, borough_map: Dict = None) -> Tuple[pd.DataFrame, Dict]:
    """Encode borough names. Pass borough_map=None during training to create it,
    pass the saved map during serving to ensure consistent encoding."""

    if borough_map is None:
        boroughs = sorted(df["borough"].unique())
        borough_map = {b: i for i, b in enumerate(boroughs)}

    df["borough_encoded"] = df["borough"].map(borough_map)
    return df, borough_map

def build_targets(pollutants: List[str], df: pd.DataFrame) -> pd.DataFrame:
    """Build target columns for model training only"""

    target_cols = {}
    for pollutant in pollutants:
        for horizon in [4, 8, 12]:
            target_cols[f"target_{pollutant}_{horizon}h"] = df.groupby("borough")[pollutant].shift(-horizon)

    return pd.concat([df, pd.DataFrame(target_cols, index=df.index)], axis=1)

def get_feature_columns(df: pd.DataFrame) -> List[str]:
    """Get feature columns by dropping targets and non-feature cols"""

    return [
        col for col in df.columns
        if not col.startswith("target")
        and col not in NON_FEATURE_COLS
    ]

def _build_core_features(df: pd.DataFrame, borough_map: Dict = None) -> Tuple[pd.DataFrame, Dict]:
    """Shared feature building logic. Called by both training and serving entry points."""

    df = build_temporal_features(df)
    df = build_lag_features(POLLUTANTS, df)
    df = build_rolling_features(POLLUTANTS, df)
    df = build_wind_features(df)
    df, borough_map = build_borough_encodings(df, borough_map)
    return df, borough_map

def build_features_for_training(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
    """Training entry point. Builds targets, drops NaN, returns borough_map for saving."""

    df, borough_map = _build_core_features(df, borough_map=None)
    df = build_targets(POLLUTANTS, df)
    df = df.dropna()
    return df, borough_map

def build_features_for_serving(df: pd.DataFrame, borough_map: Dict) -> pd.DataFrame:
    """Serving entry point. No targets, no dropna. Requires borough_map loaded from S3."""

    df, _ = _build_core_features(df, borough_map)
    return df


if __name__ == "__main__":
    df = pd.read_parquet("data/processed/cleaned_data.parquet")
    df = df.sort_values(["borough", "timestamp"]).reset_index(drop=True)
    df, borough_map = build_features_for_training(df)
    df.to_parquet("data/processed/all_boroughs_features.parquet")
    print(f"Saved {len(df)} rows with {len(df.columns)} columns")