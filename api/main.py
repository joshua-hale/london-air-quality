import logging
from fastapi import FastAPI
import asyncio
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes import health, boroughs
from redis import asyncio as aioredis
from redis.exceptions import RedisError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from config.config import settings
from config.rate_limit import limiter

# Create Logger
logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events ran at start up and shut down"""

    app.state.redis = aioredis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        decode_responses=True,
        max_connections=50,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True,
        health_check_interval=30
        )
    
    # Retry connection with exponential backoff
    max_retries = 5
    retry_delay = 3
    for attempt in range(1, max_retries + 1):
        try:
            # Test redis connection before accepting requests
            await app.state.redis.ping()
            logger.info(f"Redis connected succesfully (attempt: {attempt}/{max_retries})")
            break

        except RedisError as e:
            # Final attempt failed - give up
            if attempt == max_retries:
                logger.exception(f"Failed to connect to Redis after {max_retries} attempts")
                await app.state.redis.aclose()
                raise

            # Not final attempt - retry
            logger.warning(
                f"Redis connection failed (attempt {attempt}/{max_retries}): {e} "
                f"Retrying in {retry_delay} seconds..."
            )

            # Wait before tring to connect again
            await asyncio.sleep(retry_delay)
            retry_delay *= 1.5

    try:
        # App runs here
        yield
    finally:
        # Clean up on shutdown/errors
        await app.state.redis.aclose()
        logger.info("Redis client closed")

# Create FastAPI app 
app = FastAPI(
    title="London Air Quality API",
    description="Real-time air quality data for London boroughs",
    version="1.0.0",
    lifespan=lifespan  
)

# Add limiter state and exception handling
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"]
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(boroughs.router, prefix="/api", tags=["Boroughs"])

@app.get("/")
async def root():
    """API root"""
    return {
        "service": "London Air Quality API",
        "status": "running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)