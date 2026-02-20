import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import time
import pandas as pd
from httpx import Client
from typing import Dict, List
from data.borough_data import LONDON_MONITORING_POINTS

URL = "https://air-quality-api.open-meteo.com/v1/air-quality"

def fetch_borough_pollution_data(location: Dict) -> pd.DataFrame:
    """Fetch pollution data over a year for a single borough and return a Dataframe"""

    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "hourly": "pm2_5,pm10,nitrogen_dioxide,ozone,sulphur_dioxide,european_aqi",
        "start_date": "2025-02-20",
        "end_date": "2026-02-19"
    }

    response = Client().get(URL, params=params)

    data = response.json()

    df = pd.DataFrame(data["hourly"])
    df = df.rename(columns={"time": "timestamp", "nitrogen_dioxide": "no2", "ozone": "o3", "sulphur_dioxide": "so2"})
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["borough"] = location["borough"]
    df["latitude"] = location["lat"]
    df["longitude"] = location["lon"]

    return df

def fetch_all_pollution_data(locations: List[Dict]) -> pd.DataFrame:
    """Fetches all boroughs pollution data and returns a single Dataframe"""

    all_dfs = []

    for location in locations:
        df = fetch_borough_pollution_data(location)
        all_dfs.append(df)
        time.sleep(0.1)

    return pd.concat(all_dfs, ignore_index=True)

if __name__ == "__main__":
    df = fetch_all_pollution_data(LONDON_MONITORING_POINTS)
    df.to_parquet("data/raw/pollution/all_boroughs_2025-2026.parquet")
    print(f"Saved {len(df)} rows to parquet")




    