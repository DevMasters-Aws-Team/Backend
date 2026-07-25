from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_login_flow():
    res = client.post("/api/v1/auth/login", json={"dni": "47281930", "password": "password123"})
    assert res.status_code == 200
    assert res.json()["dni"] == "47281930"

def test_biometric_verify():
    res = client.post("/api/v1/biometric/verify", json={"dni": "47281930", "full_name": "Carlos Mendoza"})
    assert res.status_code == 200
    assert res.json()["verified"] is True

def test_checkout_flow():
    res = client.post("/api/v1/purchase/checkout", json={
        "dni": "47281930",
        "cart_id": "cart-101",
        "items": [{"product_id": "prod-101", "quantity": 1}],
        "total_amount": 199.90
    })
    assert res.status_code == 200
    assert res.json()["status"] == "CHECKOUT_COMPLETED"

def test_payment_flow():
    res = client.post("/api/v1/sales/pay", json={
        "order_id": "ord-101",
        "dni": "47281930",
        "amount": 199.90,
        "card_number_masked": "****-****-****-1234"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "APPROVED"
