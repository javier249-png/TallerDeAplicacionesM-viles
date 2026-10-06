from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "v2"}

def test_get_feed_unauthenticated():
    response = client.get("/api/v2/feed/")
    assert response.status_code == 200