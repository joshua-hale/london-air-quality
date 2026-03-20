# api/routers/predictions_8h.py

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
        predictions_json, last_updated = await redis.mget("predictions:8h", "pipeline:last_run")

        if predictions_json is None:
            logger.warning("8h predictions cache empty — returning 503")
            raise HTTPException(
                status_code=503,
                detail="8h predictions not available yet, try again in a moment"
            )

        if last_updated:
            etag = f'"{last_updated}:8h"'

            if request.headers.get("if-none-match") == etag:
                logger.info("ETag match — returning 304")
                return Response(status_code=304)

            response.headers["ETag"] = etag

        response.headers["Cache-Control"] = "public, max-age=300"

        return Response(content=predictions_json, media_type="application/json")

    except HTTPException:
        raise
    except RedisError:
        logger.exception("Redis unavailable in get_predictions_8h")
        raise HTTPException(status_code=503, detail="Cache unavailable")
    except Exception:
        logger.exception("Error in get_predictions_8h")
        raise HTTPException(status_code=500, detail="Internal server error")