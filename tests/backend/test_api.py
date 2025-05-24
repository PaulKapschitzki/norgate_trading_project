import pytest
from fastapi.testclient import TestClient
from webapp.backend.main import app
from webapp.backend.models.screener_status_new import ScreenerStatus

client = TestClient(app)

def test_api_health():
    """Teste, ob die API erreichbar ist"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_screener_status_endpoint():
    """Teste den Screener-Status-Endpoint"""
    response = client.get("/api/screener/status")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "status" in data
    assert "progress" in data
    assert "is_running" in data
    assert isinstance(data["progress"], dict)
    assert "total_symbols" in data["progress"]
    assert "processed_symbols" in data["progress"]

def test_screener_stop_endpoint():
    """Teste den Screener-Stop-Endpoint"""
    response = client.post("/api/screener/stop")
    assert response.status_code in [200, 202]