from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from env variables"""

    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379

    # OpenWeather API Configuration
    openweather_api_key: str 
    openweather_base_url: str = "http://api.openweathermap.org/data/2.5"
    api_timeout: float = 10.0

    # Rate Limiting
    api_batch_size: int = 50 
    api_batch_delay: float = 60.0 

    # Poller Configuration
    poller_schedule_minutes: int = 30

    # Logging
    log_level: str = "INFO"

    # Override from .env / REDIS_HOST or redis_host both work / Ignore unknown env vars
    model_config = SettingsConfigDict(
        env_file=".env",             
        env_file_encoding="utf-8",
        case_sensitive=False,        
        extra="ignore"             
    )

settings = Settings()

