from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class LocationData(BaseModel):
    city: str = Field(..., min_length=1)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)

    @validator('city')
    def validate_city(cls, v):
        if not v.strip():
            raise ValueError('City name cannot be empty or whitespace')
        return v.strip()

class LocationResponse(BaseModel):
    request_id: str
    location: str
    status: str
    created_at: datetime
    updated_at: datetime
    response_time: Optional[float] 