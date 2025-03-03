from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class LocationData(BaseModel):
    city: str
    latitude: float
    longitude: float

class LocationResponse(BaseModel):
    request_id: str
    location: str
    status: str
    created_at: datetime
    updated_at: datetime
    response_time: Optional[float] 