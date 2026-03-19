# models/weather.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class BoroughWeather(BaseModel):
    """Current weather data for a single borough"""

    # Location
    borough: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-90, le=90)

    # Timestamp from API
    timestamp: datetime

    # Weather readings
    temperature_2m: Optional[float] = None
    relative_humidity_2m: Optional[float] = None
    surface_pressure: Optional[float] = None
    precipitation: Optional[float] = None
    wind_speed_10m: Optional[float] = None
    wind_direction_10m: Optional[float] = None
    wind_gusts_10m: Optional[float] = None
    cloud_cover_low: Optional[float] = None
    shortwave_radiation: Optional[float] = None