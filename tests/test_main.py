from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_service_status():
    response = client.get("/service")
    assert response.status_code == 200
    assert response.json() == {"message": "Service is running"}

def test_submit_location():
    payload = {
        "city": "Istanbul",
        "latitude": 41.0082,
        "longitude": 28.9784
    }
    response = client.post("/service/submit", json=payload)
    assert response.status_code == 200
    assert "request_id" in response.json()
    assert response.json()["status"] == "received"
