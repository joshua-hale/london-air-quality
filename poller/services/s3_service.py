# services/s3_service.py

import logging
import s3fs
import pandas as pd
from typing import List
from models.borough import Borough
from models.weather import BoroughWeather
from config.config import settings

logger = logging.getLogger(__name__)

PARQUET_COLUMNS = [
    "timestamp", "pm2_5", "pm10", "no2", "o3", "so2", "european_aqi",
    "borough", "latitude", "longitude",
    "temperature_2m", "relative_humidity_2m", "surface_pressure", "precipitation",
    "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
    "cloud_cover_low", "shortwave_radiation"
]

fs = s3fs.S3FileSystem()

def append_to_s3_parquet(boroughs: List[Borough], weather_data: List[BoroughWeather]) -> None:
    """Merge pollution and weather readings and append to per-borough S3 parquets."""

    if not boroughs or not weather_data:
        logger.warning("No data to append to S3 — boroughs or weather list is empty")
        return

    # Build pollution DataFrame from Borough pydantic models
    pollution_df = pd.DataFrame([{
        "borough": b.borough,
        "timestamp": b.timestamp,
        "latitude": b.latitude,
        "longitude": b.longitude,
        "pm2_5": b.pm2_5,
        "pm10": b.pm10,
        "no2": b.no2,
        "o3": b.o3,
        "so2": b.so2,
        "european_aqi": b.european_aqi,
    } for b in boroughs])

    # Build weather DataFrame from BoroughWeather pydantic models
    weather_df = pd.DataFrame([{
        "borough": w.borough,
        "timestamp": w.timestamp,
        "latitude": w.latitude,
        "longitude": w.longitude,
        "temperature_2m": w.temperature_2m,
        "relative_humidity_2m": w.relative_humidity_2m,
        "surface_pressure": w.surface_pressure,
        "precipitation": w.precipitation,
        "wind_speed_10m": w.wind_speed_10m,
        "wind_direction_10m": w.wind_direction_10m,
        "wind_gusts_10m": w.wind_gusts_10m,
        "cloud_cover_low": w.cloud_cover_low,
        "shortwave_radiation": w.shortwave_radiation,
    } for w in weather_data])

    # Merge on borough + timestamp — pollution left, weather right matches training
    merged = pollution_df.merge(weather_df, on=["timestamp", "borough"], suffixes=("", "_weather"))
    merged = merged.drop(columns=["latitude_weather", "longitude_weather"])
    merged = merged[PARQUET_COLUMNS]

    if merged.empty:
        logger.warning("Merged DataFrame is empty — pollution and weather timestamps may not align")
        return

    # Append per borough parquet
    for borough, group in merged.groupby("borough"):
        path = f"s3://{settings.s3_bucket}/data/backfill/{borough}.parquet"

        try:
            existing = pd.read_parquet(path, filesystem=fs)
            combined = (
                pd.concat([existing, group])
                .drop_duplicates(subset=["timestamp"])
                .sort_values("timestamp")
                .reset_index(drop=True)
            )
            logger.info(f"Appended to existing parquet for {borough}: {len(combined)} total rows")

        except FileNotFoundError:
            combined = group.sort_values("timestamp").reset_index(drop=True)
            logger.info(f"Created new parquet for {borough}: {len(combined)} rows")

        except Exception as e:
            logger.error(f"Failed to read existing parquet for {borough}: {e}")
            continue

        try:
            combined.to_parquet(path, filesystem=fs, index=False)
        except Exception as e:
            logger.error(f"Failed to write parquet for {borough}: {e}")
            continue

    logger.info(f"S3 parquet update complete for {len(merged['borough'].unique())} boroughs")