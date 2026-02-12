import redis
import json
from typing import List, Dict
from datetime import datetime, timezone
from poller.models.individualborough import IndividualBorough
from poller.config.config import settings

def write_borough_data_to_redis(boroughs: List[IndividualBorough]):
    """
    Write borough pollution data to redis

    Stores:
    - boroughs:latest → JSON array of all boroughs
    - meta:borough_last_updated → ISO timestamp
    - meta:borough_count → Number of boroughs
    """

    #Connect to redis
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    # Convert borough data to dictionaries
    borough_data = [borough.model_dump() for borough in boroughs]

    # Convert to JSON string
    boroughs_json = json.dumps(borough_data, default=str)

    # Write to redis
    client.set("boroughs:latest", boroughs_json)
    client.set("meta:borough_last_updated", datetime.now(timezone.utc).isoformat())
    client.set("meta:borough_count", len(boroughs))


def get_boroughs_from_redis() -> List[IndividualBorough]:
    """Read borough pollution data from redis cache"""

    #Connect to redis
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    # Get data from redis
    boroughs_json = client.get("boroughs:latest")

    if boroughs_json is None:
        raise ValueError("No borough data points in redis cache")
    
    # Parse JSON
    boroughs_data = json.loads(boroughs_json)

    # Convert dictionary into IndividualBorough object
    boroughs = [IndividualBorough(**data) for data in boroughs_data]

    return boroughs


def get_borough_cache_metadata() -> Dict:
    """Get metadata of cached borough data"""

    # Connect to redis
    client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)

    return {
        "last_updated": client.get("meta:borough_last_updated"),
        "borough_count": client.get("meta:borough_count")
    }






