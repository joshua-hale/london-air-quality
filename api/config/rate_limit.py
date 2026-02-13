from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from config.config import settings

def get_client_ip(request: Request) -> str:
    """Get the real client IP address from behind ALB"""

    # Try X-Forwarded-For header
    forwarded_for = request.headers.get("X-Forwarded-For")

    # Get client IP if valid forwarded for header
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
        return client_ip
    
    # Some proxies use X-Real-IP
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to direct connection IP (If not using ALB)
    if request.client:
        return request.client.host
    
    # Last resort fallback
    return "unknown"

# Create limiter with custom key to get IP behind proxy
limiter = Limiter(
    key_func=get_client_ip,
    storage_uri=f"redis://{settings.redis_host}:{settings.redis_port}/1"
)

