from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class LocationData(BaseModel):
    city: str = Field(
        ..., 
        min_length=1, 
        description="Name of the city",
        example="New York"
    )
    latitude: float = Field(
        ..., 
        ge=-90, 
        le=90, 
        description="Latitude between -90 and 90",
        example=40.7128
    )
    longitude: float = Field(
        ..., 
        ge=-180, 
        le=180, 
        description="Longitude between -180 and 180",
        example=-74.0060
    )

    @validator('city')
    def validate_city(cls, v):
        if not v.strip():
            raise ValueError('City name cannot be empty or whitespace')
        return v.strip()

    @validator('latitude')
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v

    @validator('longitude')
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v

    class Config:
        schema_extra = {
            "example": {
                "city": "New York",
                "latitude": 40.7128,
                "longitude": -74.0060
            }
        }

class LocationResponse(BaseModel):
    request_id: str
    location: str
    status: str
    created_at: datetime
    updated_at: datetime
    response_time: Optional[float] 
