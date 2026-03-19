import logging
from typing import Dict
from data.borough_data import LONDON_MONITORING_POINTS
from services.openmeteo_client import fetch_all_boroughs_with_weather_sync
from services.borough_cache_service import write_borough_data_to_redis
from services.s3_service import append_to_s3_parquet

logger = logging.getLogger(__name__)

def run_poller() -> Dict:
    """
    Fetch live pollution and weather data. 
    Write pollution to Redis. 
    Append merged data to S3.
    """

    # Fetch pollution and weather concurrently for all boroughs
    boroughs, weather_data = fetch_all_boroughs_with_weather_sync(LONDON_MONITORING_POINTS)

    if not boroughs:
        raise ValueError("No borough data fetched")

    logger.info(f"Successfully fetched {len(boroughs)}/{len(LONDON_MONITORING_POINTS)} boroughs")

    # Write live pollution to Redis to serve boroughs endpoint
    write_borough_data_to_redis(boroughs)
    logger.info(f"Cached {len(boroughs)} boroughs to Redis")

    # Append merged pollution + weather to S3 to serve ML pipeline
    if weather_data:
        append_to_s3_parquet(boroughs, weather_data)
        logger.info(f"Appended {len(weather_data)} weather readings to S3")
    else:
        logger.warning("No weather data returned — S3 parquets not updated this run")

    return {
        "boroughs_cached": len(boroughs),
        "weather_appended": len(weather_data)
    }