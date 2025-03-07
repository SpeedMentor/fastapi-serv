from fastapi import APIRouter, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
import logging
from ..services.location_service import LocationService
from ..models.location_model import LocationData, LocationResponse
import os
import json

logger = logging.getLogger(__name__)
router = APIRouter()

# API Key Security
API_KEY = os.getenv("API_KEY", "secure-api-key")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

class LocationController:
    def __init__(self):
        self.service = LocationService()

    async def submit_location(self, data: LocationData):
        try:
            # Log the incoming data
            logger.info(f"Received location data: {data.dict()}")
            return self.service.submit_location(data)
        except Exception as e:
            logger.error(f"Error in submit_location: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_request_status(self, request_id: str):
        try:
            return self.service.get_request_status(request_id)
        except Exception as e:
            logger.error(f"Error in get_request_status: {str(e)}")
            raise HTTPException(status_code=404, detail=str(e))

# Create controller instance
controller = LocationController()

# Define routes
@router.post("/submit", dependencies=[Depends(verify_api_key)])
async def submit_location(data: LocationData):
    try:
        # Log the raw request data
        logger.info(f"Raw request data: {data.dict()}")
        return await controller.submit_location(data)
    except Exception as e:
        logger.error(f"Validation error: {str(e)}")
        raise

@router.get("/request-{request_id}", dependencies=[Depends(verify_api_key)])
async def get_request_status(request_id: str):
    return await controller.get_request_status(request_id) 