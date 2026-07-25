from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_simulator_burst():
    res = client.post("/api/simulator/generate-burst?count=5")
    assert res.status_code == 200
    assert res.json()["count"] == 5

def test_chaos_endpoints():
    res = client.post("/chaos/timeout?service=purchase-service")
    assert res.status_code == 503
