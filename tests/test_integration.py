import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.services.location_service import LocationService
from src.repositories.location_repository import LocationRepository
from unittest.mock import patch, MagicMock
import asyncio

client = TestClient(app)

@pytest.fixture
def mock_db():
    with patch('src.repositories.location_repository.LocationRepository') as mock:
        mock_instance = mock.return_value
        mock_instance.create_location.return_value = True
        mock_instance.get_location.return_value = ("test-id", "Test Location", "test")
        mock_instance.update_response_time.return_value = True
        mock_instance.delete_location.return_value = True
        yield mock

@pytest.fixture
def mock_service():
    with patch('src.controllers.location_controller.LocationService') as mock:
        mock_instance = mock.return_value
        mock_instance.submit_location.return_value = {
            "request_id": "test-id-123",
            "status": "received",
            "response_time": 1.5
        }
        mock_instance.get_request_status.return_value = {
            "request_id": "test-id-123",
            "status": "completed"
        }
        yield mock

@pytest.mark.skip(reason="Database connection required")
def test_end_to_end_flow(mock_db, mock_service):
    # Test data
    test_data = {
        "city": "Istanbul",
        "latitude": 41.0082,
        "longitude": 28.9784
    }
    
    # Submit location
    response = client.post(
        "/service/submit",
        json=test_data,
        headers={"X-API-Key": "secure-api-key"}
    )
    assert response.status_code == 200
    assert "request_id" in response.json()
    assert response.json()["status"] == "received"
    request_id = response.json()["request_id"]
    
    # Get status
    status_response = client.get(
        f"/service/request-{request_id}",
        headers={"X-API-Key": "secure-api-key"}
    )
    assert status_response.status_code == 200
    assert status_response.json()["request_id"] == "test-id-123"
    assert status_response.json()["status"] == "completed"

@pytest.mark.asyncio
async def test_websocket_stream():
    with client.websocket_connect("/service/stream") as websocket:
        # Test multiple messages
        for i in range(3):
            data = websocket.receive_text()
            assert "Received data:" in data

def test_error_handling():
    # Test invalid city
    invalid_data = {
        "city": "",  # Empty city
        "latitude": 41.0082,
        "longitude": 28.9784
    }
    response = client.post(
        "/service/submit",
        json=invalid_data,
        headers={"X-API-Key": "secure-api-key"}
    )
    assert response.status_code == 422  # Validation error
    
    # Test invalid coordinates
    invalid_coords = {
        "city": "Istanbul",
        "latitude": 91.0,  # Invalid latitude
        "longitude": 181.0  # Invalid longitude
    }
    response = client.post(
        "/service/submit",
        json=invalid_coords,
        headers={"X-API-Key": "secure-api-key"}
    )
    assert response.status_code == 422

def test_rate_limiting():
    # Test multiple requests in short time
    for _ in range(5):  # Assuming rate limit is 5 requests per minute
        response = client.get(
            "/service",
            headers={"X-API-Key": "secure-api-key"}
        )
        assert response.status_code == 200
    
    # Next request should be rate limited
    response = client.get(
        "/service",
        headers={"X-API-Key": "secure-api-key"}
    )
    assert response.status_code == 429  # Too Many Requests

@pytest.mark.skip(reason="Database connection required")
def test_database_operations(mock_db):
    # Test database operations
    repo = LocationRepository()
    
    # Test create
    assert repo.create_location("test-id", "Test Location", "test")
    
    # Test read
    result = repo.get_location("test-id")
    assert result is not None
    assert result[0] == "test-id"
    
    # Test update
    assert repo.update_response_time("test-id", 2.0)
    
    # Test delete
    assert repo.delete_location("test-id")
    assert repo.get_location("test-id") is None

@pytest.mark.skip(reason="Database connection required")
def test_service_layer_operations(mock_service):
    service = LocationService()
    
    # Test location submission
    result = service.submit_location({
        "city": "Istanbul",
        "latitude": 41.0082,
        "longitude": 28.9784
    })
    assert "request_id" in result
    assert result["status"] == "received"
    
    # Test status retrieval
    status = service.get_request_status("test-id")
    assert status is not None
    assert "status" in status 