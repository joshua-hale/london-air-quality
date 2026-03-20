import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from env variables"""

    # Redis Configuration
    redis_host: str
    redis_port: int = 6379

    # S3 Configuration
    s3_bucket: str
    s3_endpoint_url: Optional[str] = None
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None


    # Open-Meteo API Configuration
    openmeteo_base_url: str = "https://air-quality-api.open-meteo.com/v1"
    openmeteo_weather_url: str = "https://api.open-meteo.com/v1"
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