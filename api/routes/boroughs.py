import json
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from redis import asyncio as aioredis
from redis.exceptions import RedisError
from config.redis_dependency import get_redis_client
from config.rate_limit import limiter

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/boroughs")
@limiter.limit("5000/minute")
@limiter.limit("100000/hour")
async def get_all_boroughs(request: Request, response: Response, redis: aioredis.Redis=Depends(get_redis_client)):
    """Get air pollution data for all London boroughs"""

    try:
        # Get boroughs and last_updated JSON data from redis in single round trip
        boroughs_json, last_updated = await redis.mget("boroughs:latest", "meta:borough_last_updated")

        # Error handling for empty redis read
        if boroughs_json is None:
            logger.warning("Cache is empty - returning 503")
            raise HTTPException(
                status_code=503,
                detail="Borough data not available yet try again in a moment"
            )

        # Build response headers Cache-Control is always included
        headers = {"Cache-Control": "public, max-age=60"}

        # ETag validation logic 
        if last_updated:
            etag = f'"{last_updated}"'

            # Return 304 Not Modified if client already has current version
            if request.headers.get("if-none-match") == etag:
                logger.info("ETag match - returning 304")
                return Response(status_code=304)

            # Add ETag to response headers for client caching
            headers["ETag"] = etag

        # Return raw JSON received from redis with cache headers
        return Response(
            content=boroughs_json,
            media_type="application/json",
            headers=headers
        )

    except HTTPException:
        raise
    except RedisError:
        logger.exception("Redis unavailable in get_all_boroughs")
        raise HTTPException(
            status_code=503,
            detail="Cache unavailable"
        )
    except Exception as e:
        logger.exception("Error in get_all_boroughs")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )