from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Borough(BaseModel):
    """Borough level air quality data from Open-Meteo API"""

    # Location
    borough: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-90, le=90)

    # Timestamp from API
    timestamp: datetime

    # European Air Quality Index
    european_aqi: Optional[int] = None

    # Pollutant concentrations (μg/m³)
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None