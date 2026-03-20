import json
import pytest
from unittest.mock import AsyncMock
from httpx import AsyncClient, ASGITransport
from redis.exceptions import RedisError

# Sample test data
SAMPLE_BOROUGHS = json.dumps([
    {
        "borough": "Hackney",
        "latitude": 51.545,
        "longitude": -0.0553,
        "timestamp": "2026-03-20T12:00:00+00:00",
        "european_aqi": 45,
        "pm2_5": 12.4,
        "pm10": 18.2,
        "no2": 31.1,
        "o3": 54.3,
        "so2": 1.2
    },
    {
        "borough": "Tower Hamlets",
        "latitude": 51.5099,
        "longitude": -0.0059,
        "timestamp": "2026-03-20T12:00:00+00:00",
        "european_aqi": 52,
        "pm2_5": 15.1,
        "pm10": 20.3,
        "no2": 38.4,
        "o3": 48.2,
        "so2": 1.8
    }
])

SAMPLE_PREDICTIONS_4H = json.dumps([
    {
        "borough": "Hackney",
        "latitude": 51.545,
        "longitude": -0.0553,
        "timestamp": "2026-03-20T12:00:00+00:00",
        "valid_at": "2026-03-20T16:00:00+00:00",
        "european_aqi": 47.5,
        "pm2_5": 13.1,
        "pm10": 19.0,
        "no2": 32.4,
        "o3": 55.1,
        "so2": 1.3
    }
])

SAMPLE_PREDICTIONS_8H = json.dumps([
    {
        "borough": "Hackney",
        "latitude": 51.545,
        "longitude": -0.0553,
        "timestamp": "2026-03-20T12:00:00+00:00",
        "valid_at": "2026-03-20T20:00:00+00:00",
        "european_aqi": 51.2,
        "pm2_5": 14.8,
        "pm10": 20.1,
        "no2": 35.7,
        "o3": 52.3,
        "so2": 1.5
    }
])

LAST_UPDATED = "2026-03-20T12:00:00+00:00"
PIPELINE_LAST_RUN = "2026-03-20T12:00:00+00:00"


def make_mock_redis(mget_return_value):
    """Helper to create a mock Redis client with a given mget return value."""
    mock_redis = AsyncMock()
    mock_redis.mget = AsyncMock(return_value=mget_return_value)
    return mock_redis


@pytest.fixture
def app():
    """Create FastAPI app with all routers registered."""
    from fastapi import FastAPI
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from routes.boroughs import router as boroughs_router
    from routes.predictions_4h import router as predictions_4h_router
    from routes.predictions_8h import router as predictions_8h_router

    limiter = Limiter(key_func=get_remote_address)
    app = FastAPI()
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.include_router(boroughs_router, prefix="/api")
    app.include_router(predictions_4h_router, prefix="/api")
    app.include_router(predictions_8h_router, prefix="/api")
    return app


# ============================================================
# /api/boroughs
# ============================================================

@pytest.mark.asyncio
async def test_boroughs_returns_200_with_data(app):
    """Returns 200 and borough JSON when Redis has data."""
    mock_redis = make_mock_redis([SAMPLE_BOROUGHS, LAST_UPDATED])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/boroughs")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["borough"] == "Hackney"


@pytest.mark.asyncio
async def test_boroughs_returns_503_when_cache_empty(app):
    """Returns 503 when boroughs:latest is None in Redis."""
    mock_redis = make_mock_redis([None, None])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/boroughs")

    assert response.status_code == 503
    assert "not available" in response.json()["detail"]


@pytest.mark.asyncio
async def test_boroughs_returns_503_on_redis_error(app):
    """Returns 503 when Redis raises RedisError."""
    mock_redis = AsyncMock()
    mock_redis.mget = AsyncMock(side_effect=RedisError("Connection refused"))
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/boroughs")

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"]


@pytest.mark.asyncio
async def test_boroughs_cache_control_header(app):
    """Response includes Cache-Control header."""
    mock_redis = make_mock_redis([SAMPLE_BOROUGHS, LAST_UPDATED])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/boroughs")

    assert "cache-control" in response.headers
    assert "public" in response.headers["cache-control"]


@pytest.mark.asyncio
async def test_boroughs_returns_etag_header(app):
    """Response includes ETag header when last_updated is present."""
    mock_redis = make_mock_redis([SAMPLE_BOROUGHS, LAST_UPDATED])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/boroughs")

    assert "etag" in response.headers
    assert LAST_UPDATED in response.headers["etag"]


@pytest.mark.asyncio
async def test_boroughs_returns_304_on_etag_match(app):
    """Returns 304 Not Modified when client sends matching ETag."""
    mock_redis = make_mock_redis([SAMPLE_BOROUGHS, LAST_UPDATED])
    app.state.redis = mock_redis

    etag = f'"{LAST_UPDATED}"'

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/boroughs", headers={"if-none-match": etag})

    assert response.status_code == 304


# ============================================================
# /api/predictions/4h
# ============================================================

@pytest.mark.asyncio
async def test_predictions_4h_returns_200_with_data(app):
    """Returns 200 and prediction JSON when Redis has data."""
    mock_redis = make_mock_redis([SAMPLE_PREDICTIONS_4H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/4h")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["borough"] == "Hackney"
    assert "valid_at" in data[0]


@pytest.mark.asyncio
async def test_predictions_4h_returns_503_when_cache_empty(app):
    """Returns 503 when predictions:4h is None in Redis."""
    mock_redis = make_mock_redis([None, None])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/4h")

    assert response.status_code == 503
    assert "not available" in response.json()["detail"]


@pytest.mark.asyncio
async def test_predictions_4h_returns_503_on_redis_error(app):
    """Returns 503 when Redis raises RedisError."""
    mock_redis = AsyncMock()
    mock_redis.mget = AsyncMock(side_effect=RedisError("Connection refused"))
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/4h")

    assert response.status_code == 503


@pytest.mark.asyncio
async def test_predictions_4h_returns_etag_header(app):
    """Response includes ETag header scoped to 4h horizon."""
    mock_redis = make_mock_redis([SAMPLE_PREDICTIONS_4H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/4h")

    assert "etag" in response.headers
    assert "4h" in response.headers["etag"]


@pytest.mark.asyncio
async def test_predictions_4h_returns_304_on_etag_match(app):
    """Returns 304 Not Modified when client sends matching ETag."""
    mock_redis = make_mock_redis([SAMPLE_PREDICTIONS_4H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis

    etag = f'"{PIPELINE_LAST_RUN}:4h"'

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/4h", headers={"if-none-match": etag})

    assert response.status_code == 304


# ============================================================
# /api/predictions/8h
# ============================================================

@pytest.mark.asyncio
async def test_predictions_8h_returns_200_with_data(app):
    """Returns 200 and prediction JSON when Redis has data."""
    mock_redis = make_mock_redis([SAMPLE_PREDICTIONS_8H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/8h")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["borough"] == "Hackney"
    assert "valid_at" in data[0]


@pytest.mark.asyncio
async def test_predictions_8h_returns_503_when_cache_empty(app):
    """Returns 503 when predictions:8h is None in Redis."""
    mock_redis = make_mock_redis([None, None])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/8h")

    assert response.status_code == 503
    assert "not available" in response.json()["detail"]


@pytest.mark.asyncio
async def test_predictions_8h_returns_503_on_redis_error(app):
    """Returns 503 when Redis raises RedisError."""
    mock_redis = AsyncMock()
    mock_redis.mget = AsyncMock(side_effect=RedisError("Connection refused"))
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/8h")

    assert response.status_code == 503


@pytest.mark.asyncio
async def test_predictions_8h_returns_etag_header(app):
    """Response includes ETag header scoped to 8h horizon."""
    mock_redis = make_mock_redis([SAMPLE_PREDICTIONS_8H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/8h")

    assert "etag" in response.headers
    assert "8h" in response.headers["etag"]


@pytest.mark.asyncio
async def test_predictions_8h_returns_304_on_etag_match(app):
    """Returns 304 Not Modified when client sends matching ETag."""
    mock_redis = make_mock_redis([SAMPLE_PREDICTIONS_8H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis

    etag = f'"{PIPELINE_LAST_RUN}:8h"'

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/predictions/8h", headers={"if-none-match": etag})

    assert response.status_code == 304


# ============================================================
# Cross-endpoint consistency
# ============================================================

@pytest.mark.asyncio
async def test_4h_and_8h_etags_are_different(app):
    """4h and 8h endpoints return different ETags for the same pipeline run."""
    mock_redis_4h = make_mock_redis([SAMPLE_PREDICTIONS_4H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis_4h

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response_4h = await client.get("/api/predictions/4h")

    mock_redis_8h = make_mock_redis([SAMPLE_PREDICTIONS_8H, PIPELINE_LAST_RUN])
    app.state.redis = mock_redis_8h

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response_8h = await client.get("/api/predictions/8h")

    assert response_4h.headers["etag"] != response_8h.headers["etag"]