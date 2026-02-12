from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MonitoringPoint(BaseModel):
    """Single air quality monitoring point from OpenWeather API"""
    #Location Info
    location_name: str
    borough: str
    location_type:str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-90, le=90)

    # Timestamp
    timestamp: datetime

    # Air Quality Index (1-5 scale from OpenWeather)
    aqi: Optional[int] = Field(None, ge=1, le=5)

    # Individual Pollutant Metrics
    co: Optional[float] = None
    no: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    nh3: Optional[float] = None
