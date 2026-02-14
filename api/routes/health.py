import logging
from fastapi import APIRouter, Depends, Response
from redis import asyncio as aioredis
from redis.exceptions import RedisError
from config.redis_dependency import get_redis_client

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check(redis: aioredis.Redis = Depends(get_redis_client)):
    """Health check endpoint for ALB/ECS monitoring"""

    try:
        # Test redis connection
        await redis.ping()

        # Check if cache has data
        borough_count = await redis.get("meta:borough_count")

        # Redis works but cache is empty (waiting for poller)
        if borough_count is None:
            logger.warning("Health check: Cache is empty")
            return {
                "status": "degraded",
                "redis": "connected",
                "cache": "empty",
                "message": "Waiting for poller to populate data"
            }
        
        # Service is healthy
        logger.debug("Health check: All systems operational")
        return {
            "status": "healthy",
            "redis": "connected",
            "cache": "populated",
            "boroughs_cached": int(borough_count)
        }
    
    except RedisError as e:
        logger.exception("Health check failed: Redis error")
        return Response(
            status_code=503,
            content='{"status":"unhealthy","redis":"disconnected","error":"Cannot connect to cache"}',
            media_type="application/json"
        )
    except Exception as e:
        logger.exception("Health check failed: Unexpected error")
        return Response(
            status_code=503,
            content='{"status":"unhealthy","error":"Service unavailable"}',
            media_type="application/json"
        )

