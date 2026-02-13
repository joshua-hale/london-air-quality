from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class IndividualBorough(BaseModel):
    """Individual borough level pollution data"""

    borough_name: str
    avg_pm_25: float
    last_updated: datetime
