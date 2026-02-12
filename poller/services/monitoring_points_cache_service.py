import redis
import json
from typing import List, Dict
from datetime import datetime, timezone
from poller.models.monitoring_point import MonitoringPoint
from poller.config.config import settings

def write_monitoring_points_to_redis(monitoring_points: List[MonitoringPoint]):
    """
    Write pollution monitoring data to redis cache

    Stores:
    - monitoring_points:latest → JSON array of all monitoring points
    - meta:last_updated → ISO timestamp
    - meta:point_count → Number of monitoring points
    """

    # Connect to redis
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    # Convert station objects to dictionaries
    monitoring_point_data = [monitoring_point.model_dump() for monitoring_point in monitoring_points]

    # Convert to JSON string
    monitoring_points_json = json.dumps(monitoring_point_data, default=str)

    # Write data to redis
    client.set("monitoring_points:latest", monitoring_points_json)
    client.set("meta:last_updated", datetime.now(timezone.utc).isoformat())
    client.set("meta:point_count", len(monitoring_points))


def get_monitoring_points_from_redis() -> List[MonitoringPoint]:
    """Read pollution data from redis cache"""

    # Connect to redis 
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    # Get data from redis
    points_json = client.get("monitoring_points:latest")

    if points_json is None:
        raise ValueError("No monitoring point data in redis cache")
    
    # Parse JSON
    points_data = json.loads(points_json)

    # Convert dictionary into MonitoringPoint object
    points = [MonitoringPoint(**data) for data in points_data]

    return points


def get_monitoring_point_cache_metadata() -> Dict:
    """Get metadata on cached data"""

    # Connect to redis 
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    # Return time/count metadata
    return {
        "last_updated": client.get("meta:last_updated"),
        "point_count": client.get("meta:point_count")
    }

