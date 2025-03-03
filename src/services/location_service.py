import logging
from uuid import uuid4
from time import time
from ..repositories.location_repository import LocationRepository
from ..models.location_model import LocationData, LocationResponse

logger = logging.getLogger(__name__)

class LocationService:
    def __init__(self):
        self.repository = LocationRepository()

    def submit_location(self, data: LocationData) -> dict:
        start_time = time()
        request_id = str(uuid4())
        
        location_str = f"{data.city} ({data.latitude}, {data.longitude})"
        
        if not self.repository.create_location(request_id, location_str, "received"):
            raise Exception("Failed to create location record")

        duration = time() - start_time
        if not self.repository.update_response_time(request_id, duration):
            logger.warning(f"Failed to update response time for request {request_id}")

        logger.info(f"Location data processed: {data.city} at {data.latitude}, {data.longitude} (ID: {request_id})")
        return {
            "request_id": request_id,
            "status": "received",
            "response_time": f"{duration:.4f} sec"
        }

    def get_request_status(self, request_id: str) -> LocationResponse:
        result = self.repository.get_location(request_id)
        if not result:
            raise Exception("Request not found")

        return LocationResponse(
            request_id=result[0],
            location=result[1],
            status=result[2],
            created_at=result[3],
            updated_at=result[4],
            response_time=result[5]
        ) 