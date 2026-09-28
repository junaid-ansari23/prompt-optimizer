from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    """Test that the health endpoint returns successful status."""
    response = client.get("/health")
    
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "prompt-optimizer"
    assert "version" in data


def test_health_endpoint_structure():
    """Test that the health endpoint returns expected JSON structure."""
    response = client.get("/health")
    data = response.json()
    
    # Verify all expected keys are present
    expected_keys = {"status", "service", "version"}
    assert set(data.keys()) == expected_keys
