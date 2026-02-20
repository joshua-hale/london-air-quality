import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time
import pandas as pd
from httpx import Client
from typing import Dict, List
from data.borough_data import LONDON_MONITORING_POINTS

URL = "https://archive-api.open-meteo.com/v1/archive"

def fetch_borough_weather_data(location: Dict) -> pd.DataFrame:
    """Fetch weather data over a year for a single borough and return a Dataframe"""

    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "hourly": "temperature_2m,relative_humidity_2m,surface_pressure,precipitation,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover_low,shortwave_radiation",
        "start_date": "2025-02-20",
        "end_date": "2026-02-19"
    }

    response = Client().get(URL, params=params)

    data = response.json()

    response.raise_for_status()

    df = pd.DataFrame(data["hourly"])
    df = df.rename(columns={"time": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["borough"] = location["borough"]
    df["latitude"] = location["lat"]
    df["longitude"] = location["lon"]

    return df

def fetch_all_weather_data(locations: List[Dict]) -> pd.DataFrame:
    """Fetches all boroughs weather data and returns a single Dataframe"""

    all_dfs = []

    for location in locations:
        df = fetch_borough_weather_data(location)
        all_dfs.append(df)
        time.sleep(2)

    return pd.concat(all_dfs, ignore_index=True)

if __name__ == "__main__":
    df = fetch_all_weather_data(LONDON_MONITORING_POINTS)
    df.to_parquet("data/raw/weather/all_boroughs_2025-2026.parquet")
    print(f"Saved {len(df)} rows to parquet")




    