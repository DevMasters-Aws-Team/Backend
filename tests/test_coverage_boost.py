from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.main import app
from src.cloudwatch_client import cloudwatch_client
from src.traffic_generator import traffic_generator

client = TestClient(app)

def test_product_service_endpoint():
    res = client.get("/api/v1/products?category=Mobile")
    assert res.status_code == 200
    assert len(res.json()) > 0

def test_inventory_service_endpoint():
    res = client.post("/api/v1/inventory/reserve?dni=88776655", json={"product_id": "prod-102", "quantity": 2})
    assert res.status_code == 200
    assert res.json()["reserved"] is True

def test_address_validation_endpoint():
    res = client.post("/api/v1/address/validate", json={
        "dni": "88776655",
        "address": "Av. Arequipa 123",
        "city": "Lima",
        "zip_code": "15001"
    })
    assert res.status_code == 200
    assert res.json()["valid"] is True

def test_email_notification_endpoint():
    res = client.post("/api/v1/notifications/email?dni=88776655", json={
        "email": "test@ficticio.com",
        "subject": "Prueba de Notificacion"
    })
    assert res.status_code == 200
    assert res.json()["delivered"] is True

def test_simulator_burst_control():
    res = client.post("/api/simulator/generate-burst?count=10")
    assert res.status_code == 200
    assert res.json()["count"] == 10

    status_res = client.get("/api/simulator/status")
    assert status_res.status_code == 200

def test_chaos_500_endpoint():
    res = client.post("/chaos/error500?service=sales-service")
    assert res.status_code == 500

def test_log_inspector_filters():
    # Generate log
    client.post("/api/v1/auth/login", json={"dni": "99887766", "password": "pass"})
    
    # Filter by service
    res_svc = client.get("/api/logs?service=login-service")
    assert res_svc.status_code == 200
    
    # Filter by level
    res_lvl = client.get("/api/logs?level=INFO")
    assert res_lvl.status_code == 200

    # Filter with no match
    res_empty = client.get("/api/logs?dni=00000000")
    assert res_empty.status_code == 200
    assert len(res_empty.json()) == 0

def test_cloudwatch_flush_mock():
    with patch("src.cloudwatch_client.get_boto3_client") as mock_boto:
        mock_cw = MagicMock()
        mock_boto.return_value = mock_cw
        
        # Clear previous buffer & add 1 log
        cloudwatch_client._logs_buffer.clear()
        cloudwatch_client._logs_buffer.append({"timestamp": 12345678, "message": "{}"})
        
        flushed = cloudwatch_client.flush_to_cloudwatch()
        assert flushed == 1
        assert len(cloudwatch_client._logs_buffer) == 0
        mock_cw.put_log_events.assert_called_once()
