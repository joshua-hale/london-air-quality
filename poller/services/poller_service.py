import logging
from typing import Dict
from data.monitoring_points import LONDON_MONITORING_POINTS
from services.openweather_client import fetch_all_monitoring_points_sync
from services.borough_aggregation_service import borough_aggregator 
from services.monitoring_points_cache_service import write_monitoring_points_to_redis
from services.borough_cache_service import write_borough_data_to_redis
from exceptions.exceptions import OpenWeatherAPIError

logger = logging.getLogger(__name__)

def run_poller() -> Dict:
    """Complete poller method to fetch air quality data and write to redis cache"""

    # Fetch monitoring point data from OpenWeather API
    monitoring_points = fetch_all_monitoring_points_sync(LONDON_MONITORING_POINTS)
        
    if not monitoring_points:
        raise ValueError("No monitoring points fetched")

    logger.info(f"Successfully fetched {len(monitoring_points)}/{len(LONDON_MONITORING_POINTS)} monitoring points")
        
    # Aggregate monitoring points by borough
    boroughs = borough_aggregator(monitoring_points)  # ← Fixed function name
        
    if not boroughs:
        raise ValueError("No boroughs aggregated")
        
    logger.info(f"Successfully aggregated {len(boroughs)} boroughs")
                
    # Cache monitoring points to Redis
    write_monitoring_points_to_redis(monitoring_points)
    logger.info(f"Cached {len(monitoring_points)} monitoring points to Redis")
        
    # Cache borough aggregations to Redis
    write_borough_data_to_redis(boroughs)
    logger.info(f"Cached {len(boroughs)} borough aggregations to Redis")  

    return {
        "monitoring points": len(monitoring_points),
        "boroughs": len(boroughs)
    }    
        
        
    
