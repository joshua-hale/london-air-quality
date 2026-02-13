from fastapi import Request
from redis import asyncio as aioredis


async def get_redis_client(request: Request) -> aioredis.Redis:
    return request.app.state.redis
