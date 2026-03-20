from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import datetime, timezone, timedelta

class Borough_4h(BaseModel):
    """Pollution predictions for the 4h horizon"""

    # Location
    borough: str
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-90, le=90)

    # Timestamps
    timestamp: datetime

    @computed_field
    @property
    def valid_at(self) -> datetime:
        """Timestamp this prediction is valid for (computed_at + 4h)"""
        return self.timestamp + timedelta(hours=4)

    # European Air Quality Index
    european_aqi: Optional[float] = None

    # Pollutant concentrations (μg/m³)
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None
    o3: Optional[float] = None
    so2: Optional[float] = None