import httpx
import asyncio
import math
from typing import List, Dict
from datetime import datetime, timezone
from poller.models.monitoring_point import MonitoringPoint
from poller.config.config import settings
from poller.exceptions.exceptions import OpenWeatherAPIError

async def fetch_monitoring_point(client: httpx.AsyncClient, location: dict) -> MonitoringPoint:
    """Fetch air quality data for ONE location from OpenWeather API"""

    # Openweather api endpoint
    url = f"{settings.openweather_base_url}/air_pollution"

    # Query parameters
    params = {"lat": location["lat"], "lon": location["lon"], "appid": settings.openweather_api_key}

    # Make HTTP get request
    response = await client.get(url, params=params)

    # Raise exception if error
    response.raise_for_status()

    try:
        # Parse JSON response
        data = response.json()

        # Extract pollution components from data
        reading = data["list"][0]
        components = reading["components"]

        return MonitoringPoint (
            # Location data from preset location dict
            location_name=location["name"],      # "Westminster - Marylebone Road"
            borough=location["borough"],         # "Westminster"
            location_type=location["type"],      # "high_traffic"
            latitude=location["lat"],            # 51.522568
            longitude=location["lon"],           # -0.154611

            # Timestamp from API (convert Unix timestamp to Python datetime)
            timestamp=datetime.fromtimestamp(reading["dt"], tz=timezone.utc),

            # Air Quality Index from API (1-5 scale)
            aqi=reading["main"]["aqi"],
            
            # Pollutant concentrations from API (all in μg/m³)
            co=components.get("co"),                 
            no=components.get("no"),             
            no2=components.get("no2"),              
            o3=components.get("o3"),                
            so2=components.get("so2"),             
            pm2_5=components.get("pm2_5"),         
            pm10=components.get("pm10"),            
            nh3=components.get("nh3")           
        )

    except (KeyError, IndexError, TypeError, ValueError) as e:
        raise OpenWeatherAPIError(f"Invalid response for {location['name']}: {type(e).__name__}") from e


async def fetch_all_monitoring_points(locations: List[Dict]) -> List[MonitoringPoint]:
    """Fetch air quality for all London locations with rate limiting"""

    # List to collect succesful requests
    all_points = []

    # Get rate limiting config from env
    batch_size = settings.api_batch_size
    batch_delay = settings.api_batch_delay

    # Workout num of batches need to meet rate limiting requirements
    num_batches = math.ceil(len(locations) / batch_size)

    # Configure client timeout and connection limits
    timeout = httpx.Timeout(settings.api_timeout)
    limits = httpx.Limits(max_connections=batch_size, max_keepalive_connections=batch_size)

    # Create HTTP client and  process each batch seperately
    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        for batch_num in range(num_batches):

            # Get batch indexes
            start_index =  batch_num * batch_size
            end_index = min(start_index + batch_size, len(locations))
            batch = locations[start_index:end_index]

            # Create list of tasks (coroutines) to run for batch
            tasks = [fetch_monitoring_point(client, location) for location in batch]

            # Run all taks in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Append valid monitoring points to all_points list
            for result in results:
                if not isinstance(result, Exception):
                    all_points.append(result)

            # Apply rate limiting wait time afte processing batch
            if batch_num < num_batches - 1:
                await asyncio.sleep(batch_delay)

    # Return list of all valid monitoring points
    return all_points


def fetch_all_monitoring_points_sync(locations: List[Dict]) -> List[MonitoringPoint]:
    """Sync wrapper for fetch_all_monitoring_points method"""

    return asyncio.run(fetch_all_monitoring_points(locations))











