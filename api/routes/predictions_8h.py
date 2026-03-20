import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from redis import asyncio as aioredis
from redis.exceptions import RedisError
from config.redis_dependency import get_redis_client
from config.rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/predictions/8h")
@limiter.limit("5000/minute")
@limiter.limit("100000/hour")
async def get_predictions_8h(
    request: Request,
    response: Response,
    redis: aioredis.Redis = Depends(get_redis_client)
):
    """Get 8h air pollution predictions for all London boroughs"""

    try:
        # Get predictions and pipeline last run timestamp from redis in single round trip
        predictions_json, last_updated = await redis.mget("predictions:8h", "pipeline:last_run")

        # Error handling for empty redis read — pipeline may not have run yet
        if predictions_json is None:
            logger.warning("8h predictions cache empty — returning 503")
            raise HTTPException(
                status_code=503,
                detail="8h predictions not available yet, try again in a moment"
            )

        # Build response headers Cache-Control is always included
        # 300 seconds (5 min) matches pipeline run frequency
        headers = {"Cache-Control": "public, max-age=300"}

        # ETag validation logic
        if last_updated:
            etag = f'"{last_updated}:8h"'

            # Return 304 Not Modified if client already has current version
            if request.headers.get("if-none-match") == etag:
                logger.info("ETag match — returning 304")
                return Response(status_code=304)

            # Add ETag to response headers for client caching
            headers["ETag"] = etag

        # Return raw JSON received from redis with cache headers
        return Response(
            content=predictions_json,
            media_type="application/json",
            headers=headers
        )

    except HTTPException:
        raise
    except RedisError:
        logger.exception("Redis unavailable in get_predictions_8h")
        raise HTTPException(status_code=503, detail="Cache unavailable")
    except Exception:
        logger.exception("Error in get_predictions_8h")
        raise HTTPException(status_code=500, detail="Internal server error")