import redis
import json
from typing import List, Dict
from datetime import datetime, timezone
from models.individualborough import IndividualBorough
from config.config import settings

BOROUGH_COUNT = 33

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

    # If all boroughs have valid data write all to redis
    if len(borough_data) == BOROUGH_COUNT:

        # Convert to JSON string
        boroughs_json = json.dumps(borough_data, default=str)

        # Write to redis
        client.set("boroughs:latest", boroughs_json)
        client.set("meta:borough_last_updated", datetime.now(timezone.utc).isoformat())
        client.set("meta:borough_count", len(boroughs))

    else:
        # Get cached boroughs from redis
        existing_json = client.get("boroughs:latest")

        if existing_json:
            # Parse JSON
            existing_data = json.loads(existing_json)

            # Create a dictionary of new boroughs by name for easy lookup
            new_boroughs_dict = {borough["borough_name"]: borough for borough in borough_data}

            # Merge data by replacing old values where we have new data and keeping old data otherwise
            merged_data = []
            for old_borough in existing_data:
                borough_name = old_borough["borough_name"]
                if borough_name in new_boroughs_dict:
                    # Append new data if available
                    merged_data.append(new_boroughs_dict[borough_name])
                else:
                    # Append old data if no new data available
                    merged_data.append(old_borough)

            # Create set of existing names
            existing_names = {borough["borough_name"] for borough in existing_data}

            # Append any new data for any boroughs not in old data
            for new_borough in borough_data:
                if new_borough["borough_name"] not in existing_names:
                    merged_data.append(new_borough)
            
            # Convert merged data to JSON string
            merged_json = json.dumps(merged_data, default=str)

            # Write to redis
            client.set("boroughs:latest", merged_json)
            client.set("meta:borough_count", len(merged_data))

        else:
            # No existing cache to merge with: Write what we have to redis
            boroughs_json = json.dumps(borough_data, default=str)
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






