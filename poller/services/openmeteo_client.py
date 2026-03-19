import httpx
import asyncio
import logging
from typing import List, Dict, Tuple
from datetime import datetime, timezone
from models.borough import Borough
from models.weather import BoroughWeather
from config.config import settings
from exceptions.exceptions import OpenMeteoAPIError

logger = logging.getLogger(__name__)


async def fetch_borough(client: httpx.AsyncClient, location: dict) -> Borough:
    """Fetch air quality data for ONE location from Open Meteo API"""

    # Open Meteo api pollution data endpoint
    url = f"{settings.openmeteo_base_url}/air-quality"

    # Query parameters
    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "current": "pm2_5,pm10,nitrogen_dioxide,ozone,sulphur_dioxide,european_aqi"
    }

    # Make HTTP get request
    response = await client.get(url, params=params)

    # Raise exception if error
    response.raise_for_status()

    try:
        # Parse JSON response
        data = response.json()

        # Extract individual components from data
        components = data["current"]

        return Borough (
            # Location data from preset location dict
            borough=location["borough"],      
            latitude=location["lat"],         
            longitude=location["lon"],          

            # Timestamp from API (convert from iso format)
            timestamp=datetime.fromisoformat(components["time"]).replace(tzinfo=timezone.utc),

            # Air Quality Index from API (European AQI scale)
            european_aqi=components.get("european_aqi"),
            
            # Pollutant concentrations from API (all in μg/m³)
            pm2_5=none_if_zero(components.get("pm2_5")),         
            pm10=none_if_zero(components.get("pm10")),            
            no2=none_if_zero(components.get("nitrogen_dioxide")),              
            o3=none_if_zero(components.get("ozone")),                
            so2=none_if_zero(components.get("sulphur_dioxide"))       
        )

    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise OpenMeteoAPIError(f"Invalid response for {location['borough']}: {type(e).__name__}") from e
    

async def fetch_borough_weather(client: httpx.AsyncClient, location: dict) -> BoroughWeather:
    """Fetch current weather data for one borough from Open-Meteo forecast API"""

    # Open Meteo api weather data endpoint
    url = f"{settings.openmeteo_weather_url}/forecast"

    # Query parameters
    params = {
        "latitude": location["lat"],
        "longitude": location["lon"],
        "current": "temperature_2m,relative_humidity_2m,surface_pressure,precipitation,wind_speed_10m,wind_direction_10m,wind_gusts_10m,cloud_cover_low,shortwave_radiation",
    }

    # Make HTTP get request
    response = await client.get(url, params=params)

    # Raise exception if error
    response.raise_for_status()

    try:
        # Parse JSON response
        data = response.json()

        # Extract individual components from data
        components = data["current"]

        # Return pydantic model with current weather readings
        return BoroughWeather(
            borough=location["borough"],
            latitude=location["lat"],
            longitude=location["lon"],
            timestamp=datetime.fromisoformat(components["time"]).replace(tzinfo=timezone.utc),
            temperature_2m=components.get("temperature_2m"),
            relative_humidity_2m=components.get("relative_humidity_2m"),
            surface_pressure=components.get("surface_pressure"),
            precipitation=components.get("precipitation"),
            wind_speed_10m=components.get("wind_speed_10m"),
            wind_direction_10m=components.get("wind_direction_10m"),
            wind_gusts_10m=components.get("wind_gusts_10m"),
            cloud_cover_low=components.get("cloud_cover_low"),
            shortwave_radiation=components.get("shortwave_radiation"),
        )


    except (KeyError, IndexError, TypeError, ValueError, StopIteration) as e:
        raise OpenMeteoAPIError(f"Invalid weather response for {location['borough']}: {type(e).__name__}") from e


async def fetch_all_boroughs(locations: List[Dict]) -> List[Borough]:
    """Fetch air quality for all London locations with rate limiting"""

    # List to collect succesful requests
    all_boroughs = []

    # Get rate limiting config from env
    semaphore = asyncio.Semaphore(settings.api_batch_size)

    async def fetch_with_semaphore(client: httpx.AsyncClient, location: Dict):
        """Helper function to fetch individual borough data with semaphore"""
        async with semaphore:
            result = await fetch_borough(client, location)
            await asyncio.sleep(1)
            return result
    
    # Configure client timeout and connection limits
    timeout = httpx.Timeout(settings.api_timeout)
    limits = httpx.Limits(max_connections=settings.api_batch_size, max_keepalive_connections=settings.api_batch_size)

    # Create HTTP client and  process each batch seperately
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:

        # Create list of tasks (coroutines) to run for batch
        tasks = [fetch_with_semaphore(client, location) for location in locations]

        # Run all taks in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

    # Append valid monitoring points to all_boroughs list
    for i, result in enumerate(results):
        if not isinstance(result, Exception):
            all_boroughs.append(result)
        else:
            logger.warning(f"Fetch failed for {locations[i]['borough']}: {result}")

    # Return list of all valid monitoring points
    return all_boroughs


async def fetch_all_boroughs_with_weather(locations: List[Dict]) -> Tuple[List[Borough], List[BoroughWeather]]:
    """Fetch pollution and weather concurrently for all boroughs."""

    # Apply rate limiting config from settings
    semaphore = asyncio.Semaphore(settings.api_batch_size)
    timeout = httpx.Timeout(settings.api_timeout)
    limits = httpx.Limits(
        max_connections=settings.api_batch_size,
        max_keepalive_connections=settings.api_batch_size
    )

    # Fetch pollution and weather data concurrently
    async def fetch_both(client: httpx.AsyncClient, location: dict):
        async with semaphore:
            pollution = await fetch_borough(client, location)
            weather = await fetch_borough_weather(client, location)
            await asyncio.sleep(1)
            return pollution, weather

    # Run async ingestion tasks
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        tasks = [fetch_both(client, location) for location in locations]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    pollution_results = []
    weather_results = []

    # Iterate through results and split into assigned lists, failed boroughs skipped to not crash ingestion
    for i, result in enumerate(results):
        if not isinstance(result, Exception):
            pollution, weather = result
            pollution_results.append(pollution)
            weather_results.append(weather)
        else:
            logger.warning(f"Fetch failed for {locations[i]['borough']}: {result}")

    return pollution_results, weather_results



def fetch_all_boroughs_sync(locations: List[Dict]) -> List[Borough]:
    """Sync wrapper for fetch_all_monitoring_points method"""

    return asyncio.run(fetch_all_boroughs(locations))


def fetch_all_boroughs_with_weather_sync(locations: List[Dict]) -> Tuple[List[Borough], List[BoroughWeather]]:
    """Sync wrapper for fetch_all_boroughs_with_weather"""
    return asyncio.run(fetch_all_boroughs_with_weather(locations))


def none_if_zero(value: float):
    """Helper method to return None if value == 0"""
    if not value:
        return None
    else:
        return value











