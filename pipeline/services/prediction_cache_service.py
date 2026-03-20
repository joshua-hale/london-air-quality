import redis
import json
import logging
from datetime import datetime, timezone
from typing import Dict
from config.config import settings

logger = logging.getLogger(__name__)

def write_predictions_to_redis(all_predictions: Dict) -> None:
    """
    Write all borough predictions to Redis as two JSON arrays.

    Stores:
    - predictions:4h → JSON array of all 33 boroughs with 4h predictions
    - predictions:8h → JSON array of all 33 boroughs with 8h predictions
    """

    client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True
    )

    forecasts_4h = json.dumps(all_predictions["4h"], default=str)
    forecasts_8h = json.dumps(all_predictions["8h"], default=str)

    pipe = client.pipeline()
    pipe.set("predictions:4h", forecasts_4h)
    pipe.set("predictions:8h", forecasts_8h)
    pipe.execute()

    logger.info(f"Cached predictions for {len(all_predictions['4h'])} boroughs")


def write_pipeline_status(status: str) -> None:
    """Write pipeline run status and timestamp to Redis."""
    client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True
    )
    client.set("pipeline:status", status)
    client.set("pipeline:last_run", datetime.now(timezone.utc).isoformat())