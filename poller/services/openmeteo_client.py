import httpx
import asyncio
from typing import List, Dict
from datetime import datetime, timezone
from models.borough import Borough
from config.config import settings
from exceptions.exceptions import OpenMeteoAPIError

async def fetch_borough(client: httpx.AsyncClient, location: dict) -> Borough:
    """Fetch air quality data for ONE location from Open Meteo API"""

    # Open Meteo api endpoint
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
        for result in results:
            if not isinstance(result, Exception):
                all_boroughs.append(result)

    # Return list of all valid monitoring points
    return all_boroughs


def fetch_all_boroughs_sync(locations: List[Dict]) -> List[Borough]:
    """Sync wrapper for fetch_all_monitoring_points method"""

    return asyncio.run(fetch_all_boroughs(locations))

def none_if_zero(value: float):
    """Helper method to return None if value == 0"""
    if not value:
        return None
    else:
        return value











