import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from env variables"""

    # Redis Configuration
    redis_host: str
    redis_port: int = 6379

    # Open-Meteo API Configuration
    openmeteo_base_url: str = "https://air-quality-api.open-meteo.com/v1"
    api_timeout: float = 10.0

    # Rate Limiting
    api_batch_size: int = 5
    api_batch_delay: float = 1.0

    # Logging
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",             
        env_file_encoding="utf-8",
        case_sensitive=False,        
        extra="ignore"             
    )

settings = Settings()