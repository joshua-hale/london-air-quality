from typing import AsyncGenerator
from redis import asyncio as aioredis
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API settings loaded from environment variables."""
    
    redis_host: str = "localhost"
    redis_port: int = 6379    
    
    model_config = SettingsConfigDict(
        env_file=".env",             
        env_file_encoding="utf-8",
        case_sensitive=False,        
        extra="ignore"             
    )


settings = Settings()