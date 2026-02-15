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
@limiter.limit("100/minute")
@limiter.limit("10000/hour")
async def get_all_boroughs(request: Request, response: Response, redis: aioredis.Redis=Depends(get_redis_client)):
    """Get air pollution data for all London boroughs"""

    try:
        # Get boroughs and last_updated JSON data from redis 
        boroughs_json, last_updated = await redis.mget("boroughs:latest", "meta:borough_last_updated")

        # Error handling for empty redis read
        if boroughs_json is None:
                logger.warning("Cache is empty - returning 503")
                raise HTTPException(
                    status_code=503,
                    detail="Borough data not available yet try again in a moment"
                )

        # ETag validation logic
        if last_updated:
            etag = f'"{last_updated}"'

            if request.headers.get("if-none-match") == etag:
                logger.info("ETag match - returning 304")
                return Response(status_code=304)
            
            response.headers["ETag"] = etag

        # Cache configuration
        response.headers["Cache-Control"] = "public, max-age=600"

        # Return raw JSON recieved from redis
        return Response(content=boroughs_json, media_type="application/json")
    
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

         

    