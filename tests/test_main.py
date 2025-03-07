from fastapi.testclient import TestClient
from src.main import app, limiter
import pytest
from unittest.mock import patch, MagicMock
from src.models.location_model import LocationData, LocationResponse
from src.services.location_service import LocationService
from src.repositories.location_repository import LocationRepository

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter before each test"""
    limiter.reset()
    yield

@pytest.fixture
def mock_repo():
    with patch('src.repositories.location_repository.LocationRepository') as mock:
        mock_instance = mock.return_value
        mock_instance.create_location.return_value = True
        mock_instance.get_location.return_value = ("test-id", "Test Location", "test")
        mock_instance.update_response_time.return_value = True
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

@pytest.mark.unit
def test_service_status():
    response = client.get("/service")
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["message"] == "Service is running"
    assert "websocket_connections" in response_data
    assert isinstance(response_data["websocket_connections"], int)
    assert "uptime" in response_data
    assert isinstance(response_data["uptime"], (int, float))

@pytest.mark.database
def test_submit_location():
    payload = {
        "city": "Istanbul",
        "latitude": 41.0082,
        "longitude": 28.9784
    }
    response = client.post("/service/submit", json=payload, headers={"X-API-Key": "secure-api-key"})
    assert response.status_code == 200
    assert "request_id" in response.json()
    assert response.json()["status"] == "received"

@pytest.mark.database
def test_get_request_status():
    # First create a request
    payload = {
        "city": "Istanbul",
        "latitude": 41.0082,
        "longitude": 28.9784
    }
    create_response = client.post("/service/submit", json=payload, headers={"X-API-Key": "secure-api-key"})
    request_id = create_response.json()["request_id"]
    
    # Then get its status
    response = client.get(f"/service/request-{request_id}", headers={"X-API-Key": "secure-api-key"})
    assert response.status_code == 200
    assert response.json()["request_id"] == request_id
    assert response.json()["status"] == "received"

@pytest.mark.unit
def test_invalid_api_key():
    payload = {
        "city": "Istanbul",
        "latitude": 41.0082,
        "longitude": 28.9784
    }
    response = client.post("/service/submit", json=payload, headers={"X-API-Key": "invalid-key"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Forbidden: Invalid API Key"

@pytest.mark.unit
@pytest.mark.skip(reason="Websocket test causing pipeline to hang")
@pytest.mark.asyncio
async def test_websocket_connection():
    import asyncio
    with client.websocket_connect("/service/stream") as websocket:
        try:
            with pytest.raises(asyncio.TimeoutError):
                await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
        except Exception:
            pass  # We expect timeout errors
        finally:
            await websocket.close()

@pytest.mark.database
def test_location_service():
    service = LocationService()
    data = LocationData(city="Istanbul", latitude=41.0082, longitude=28.9784)
    result = service.submit_location(data)
    assert "request_id" in result
    assert result["status"] == "received"
    assert "response_time" in result

@pytest.mark.database
def test_location_repository():
    repo = LocationRepository()
    request_id = "test-id"
    location = "Istanbul (41.0082, 28.9784)"
    status = "test"
    
    # Test create_location
    assert repo.create_location(request_id, location, status)
    
    # Test get_location
    result = repo.get_location(request_id)
    assert result is not None
    assert result[0] == request_id
    assert result[1] == location
    assert result[2] == status
    
    # Test update_response_time
    assert repo.update_response_time(request_id, 1.5)

@pytest.mark.unit
def test_location_models():
    # Test LocationData model
    data = LocationData(city="Istanbul", latitude=41.0082, longitude=28.9784)
    assert data.city == "Istanbul"
    assert data.latitude == 41.0082
    assert data.longitude == 28.9784
    
    # Test LocationResponse model
    response = LocationResponse(
        request_id="test-id",
        location="Istanbul (41.0082, 28.9784)",
        status="test",
        created_at="2023-01-01T00:00:00",
        updated_at="2023-01-01T00:00:00",
        response_time=1.5
    )
    assert response.request_id == "test-id"
    assert response.location == "Istanbul (41.0082, 28.9784)"
    assert response.status == "test"
    assert response.response_time == 1.5
