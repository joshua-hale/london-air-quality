from redis import asyncio as aioredis
from typing import AsyncGenerator
from api.config.config import settings


async def get_redis_client() -> AsyncGenerator[aioredis.Redis, None]:
    """Dependency to get async redis client"""

    client = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5
    )

    try:
        yield client
    finally:
        await client.aclose()