# scripts/backfill.py

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time
import logging
import s3fs
import pandas as pd
from datetime import datetime, timedelta
from httpx import Client
from typing import Dict, List
from data.borough_data import LONDON_MONITORING_POINTS
from config.config import settings
from services.s3_service import PARQUET_COLUMNS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

fs = s3fs.S3FileSystem()

# 7 days backfill window
END_DATE = datetime.now().strftime("%Y-%m-%d")
START_DATE = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

POLLUTION_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_pollution(location: Dict, start: str, end: str) -> pd.DataFrame:
    """Fetch hourly pollution data for a single borough over the backfill window."""

    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "hourly": "pm2_5,pm10,nitrogen_dioxide,ozone,sulphur_dioxide,european_aqi",
        "start_date": start,
        "end_date": end
    }

    response = Client().get(POLLUTION_URL, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["hourly"])
    df = df.rename(columns={
        "time": "timestamp",
        "nitrogen_dioxide": "no2",
        "ozone": "o3",
        "sulphur_dioxide": "so2"
    })
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["borough"] = location["borough"]
    df["latitude"] = location["lat"]
    df["longitude"] = location["lon"]

    return df


def fetch_weather(location: Dict, start: str, end: str) -> pd.DataFrame:
    """Fetch hourly weather data for a single borough over the backfill window."""

    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,precipitation,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover_low,shortwave_radiation",
        "start_date": start,
        "end_date": end
    }

    response = Client().get(WEATHER_URL, params=params)
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["hourly"])
    df = df.rename(columns={"time": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["borough"] = location["borough"]
    df["latitude"] = location["lat"]
    df["longitude"] = location["lon"]

    return df


def backfill_borough(location: Dict) -> None:
    """Fetch, merge and write one week of data for a single borough to S3."""

    borough = location["borough"]
    logger.info(f"Backfilling {borough}...")

    try:
        pollution_df = fetch_pollution(location, START_DATE, END_DATE)
        weather_df = fetch_weather(location, START_DATE, END_DATE)

        # Merge matching training script exactly — pollution left, weather right
        merged = pollution_df.merge(
            weather_df,
            on=["timestamp", "borough"],
            suffixes=("", "_weather")
        )
        merged = merged.drop(columns=["latitude_weather", "longitude_weather"])

        # Enforce column order to match training parquet
        merged = merged[PARQUET_COLUMNS]

        # Verify no columns are missing before writing
        missing = [col for col in PARQUET_COLUMNS if col not in merged.columns]
        if missing:
            logger.error(f"Missing columns for {borough}: {missing} — skipping")
            return

        merged = merged.sort_values("timestamp").reset_index(drop=True)

        path = f"s3://{settings.s3_bucket}/data/backfill/{borough}.parquet"
        merged.to_parquet(path, filesystem=fs, index=False)

        logger.info(f"Backfilled {borough}: {len(merged)} rows written to {path}")

    except Exception as e:
        logger.error(f"Backfill failed for {borough}: {e}")


def run_backfill(locations: List[Dict]) -> None:
    """Run backfill for all boroughs with rate limiting."""

    logger.info(f"Starting backfill: {START_DATE} to {END_DATE}")
    logger.info(f"Backfilling {len(locations)} boroughs...")

    for i, location in enumerate(locations):
        backfill_borough(location)
        logger.info(f"Progress: {i + 1}/{len(locations)}")
        time.sleep(1)  # respect Open-Meteo rate limits

    logger.info("Backfill complete")


if __name__ == "__main__":
    run_backfill(LONDON_MONITORING_POINTS)