"""Alerts endpoints - Alertas activas del sistema."""

from fastapi import APIRouter, Query
from typing import Optional, List
from datetime import datetime, timezone, timedelta
import uuid
import random

router = APIRouter()

# Alertas simuladas en memoria
MOCK_ALERTS: List[dict] = []


def _seed_alerts():
    """Genera alertas mock si no existen."""
    if MOCK_ALERTS:
        return
    services = ["user-service", "order-service", "payment-service"]
    errors = [
        ("POST /api/users", 500, "Database connection timeout"),
        ("GET /api/orders/123", 503, "Service temporarily unavailable"),
        ("POST /api/payments", 500, "Payment gateway timeout"),
        ("GET /api/users/profile", 401, "Token expired"),
    ]
    for i in range(6):
        svc = random.choice(services)
        endpoint, code, msg = random.choice(errors)
        MOCK_ALERTS.append({
            "id": str(uuid.uuid4())[:8],
            "severity": "ERROR" if code == 500 else "WARN",
            "service": svc,
            "endpoint": endpoint,
            "status_code": code,
            "message": msg,
            "trace_id": f"trace-{uuid.uuid4().hex[:12]}",
            "timestamp": (datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 60))).isoformat(),
            "status": random.choice(["active", "active", "acknowledged"]),
        })


@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = Query(None, description="ERROR o WARN"),
    service: Optional[str] = Query(None, description="Nombre del servicio"),
    limit: int = Query(50, le=100),
):
    """Lista alertas activas con filtros opcionales."""
    _seed_alerts()
    results = MOCK_ALERTS

    if severity:
        results = [a for a in results if a["severity"] == severity.upper()]
    if service:
        results = [a for a in results if a["service"] == service]

    return {"alerts": results[:limit], "total": len(results)}


@router.get("/alerts/{alert_id}")
async def get_alert_detail(alert_id: str):
    """Detalle de una alerta con request/response."""
    _seed_alerts()
    for alert in MOCK_ALERTS:
        if alert["id"] == alert_id:
            return {
                **alert,
                "request": {
                    "method": alert["endpoint"].split(" ")[0],
                    "url": alert["endpoint"].split(" ")[1],
                    "headers": {"Authorization": "Bearer ***", "Content-Type": "application/json"},
                },
                "response": {
                    "status_code": alert["status_code"],
                    "body": {"error": alert["message"], "service": alert["service"]},
                },
            }
    return {"error": "Alert not found"}
