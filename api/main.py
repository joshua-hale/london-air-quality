import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from routes import health, boroughs
from redis import asyncio as aioredis
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
    
    try:
        # Test redis connection before accepting requests
        await app.state.redis.ping()
        logger.info("Redis client initialized with connection pool")

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