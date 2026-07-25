from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_local_log_inspector():
    # 1. Trigger a login request
    login_res = client.post("/api/v1/auth/login", json={"dni": "11223344", "password": "pass"})
    assert login_res.status_code == 200

    # 2. Search local logs by DNI
    logs_res = client.get("/api/logs?dni=11223344")
    assert logs_res.status_code == 200
    logs = logs_res.json()
    assert len(logs) > 0
    assert logs[0]["user_context"]["dni"] == "11223344"
    assert logs[0]["service"] == "login-service"
