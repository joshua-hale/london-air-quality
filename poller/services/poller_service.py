import logging
from typing import Dict
from data.borough_data import LONDON_MONITORING_POINTS
from services.openmeteo_client import fetch_all_boroughs_sync
from services.borough_cache_service import write_borough_data_to_redis
from exceptions.exceptions import OpenMeteoAPIError

logger = logging.getLogger(__name__)

def run_poller() -> Dict:
    """Complete poller method to fetch air quality data and write to redis cache"""

    # Fetch monitoring point data from Open Meteo API
    boroughs = fetch_all_boroughs_sync(LONDON_MONITORING_POINTS)
        
    # Check if fetch_all_boroughs_sync returned Borough objects
    if not boroughs:
        raise ValueError("No monitoring points fetched")

    logger.info(f"Successfully fetched {len(boroughs)}/{len(LONDON_MONITORING_POINTS)} monitoring points")                    
        
    # Cache borough aggregations to Redis
    write_borough_data_to_redis(boroughs)
    logger.info(f"Cached {len(boroughs)} boroughs to Redis")  

    # Return number of boroughs fetched by client
    return {
        "boroughs": len(boroughs)
    }    
        
        
    
