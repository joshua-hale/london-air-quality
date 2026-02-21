import pandas as pd
import numpy as np
from typing import List

POLLUTANTS = ["pm2_5", "pm10", "no2", "o3", "so2", "european_aqi"]

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

    lag_times = [1, 3, 6, 12, 24, 48, 168]

    for variable in variables:
        for lag in lag_times:
            df[f"{variable}_lag_{lag}h"] = df.groupby("borough")[variable].shift(lag)
            
    return df

def build_rolling_features(variables: List[str], df: pd.DataFrame) -> pd.DataFrame:
    """Build all rolling features required for predictions"""

    windows = [3, 6, 12, 24]

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

def build_borough_encodings(df: pd.DataFrame) -> pd.DataFrame:
    """Encodes borough name for LGBM model"""

    df["borough_encoded"] = df["borough"].astype("category").cat.codes

    return df

def build_targets(pollutants: List[str], df: pd.DataFrame) -> pd.DataFrame:
    """Build target columns for model training"""
    
    for pollutant in pollutants:
        df[f"target_{pollutant}_12h"] = df.groupby("borough")[pollutant].shift(-12)
        df[f"target_{pollutant}_24h"] = df.groupby("borough")[pollutant].shift(-24)

    return df

def build_features(pollutants: List[str], df: pd.DataFrame) -> pd.DataFrame:
    """Build all features required for LGBM model predictions"""

    df = build_temporal_features(df)
    df = build_lag_features(pollutants, df)
    df = build_rolling_features(pollutants, df)
    df = build_wind_features(df)
    df = build_borough_encodings(df)
    df = build_targets(pollutants, df)
    df = df.dropna()
    return df

if __name__ == "__main__":
    df = pd.read_parquet("data/processed/cleaned_data.parquet")
    df = df.sort_values(["borough", "timestamp"]).reset_index(drop=True)
    df = build_features(POLLUTANTS, df)
    df.to_parquet("data/processed/all_boroughs_features.parquet")
    print(f"Saved {len(df)} rows with {len(df.columns)} columns")




