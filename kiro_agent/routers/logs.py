"""Logs endpoints - Logs filtrados ERROR/WARN."""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timezone, timedelta
import random
import uuid

router = APIRouter()


@router.get("/logs")
async def get_logs(
    service: Optional[str] = Query(None, description="Filtrar por servicio"),
    level: str = Query("ERROR", description="ERROR o WARN"),
    hours: int = Query(1, description="Últimas N horas"),
    limit: int = Query(50, le=200),
):
    """Obtiene logs filtrados (solo ERROR y WARN) - simula lectura de CloudWatch."""
    services = ["user-service", "order-service", "payment-service", "auth-service"]
    error_messages = [
        "Database connection timeout after 30000ms",
        "Connection pool exhausted - max connections reached",
        "Payment gateway returned HTTP 502",
        "Token validation failed - signature mismatch",
        "Queue message processing failed - DLQ threshold exceeded",
        "Memory usage exceeded 90% threshold",
        "Service discovery timeout - endpoint unreachable",
    ]
    endpoints = [
        "POST /api/users", "GET /api/orders", "POST /api/payments",
        "GET /api/auth/verify", "POST /api/notifications",
    ]

    logs = []
    now = datetime.now(timezone.utc)
    target_services = [service] if service else services

    for i in range(min(limit, 30)):
        svc = random.choice(target_services)
        ts = now - timedelta(minutes=random.randint(1, hours * 60))
        logs.append({
            "id": str(uuid.uuid4())[:8],
            "timestamp": ts.isoformat(),
            "level": level,
            "service": svc,
            "endpoint": random.choice(endpoints),
            "status_code": 500 if level == "ERROR" else 429,
            "message": random.choice(error_messages),
            "trace_id": f"trace-{uuid.uuid4().hex[:12]}",
            "duration_ms": random.randint(100, 35000),
        })

    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"logs": logs, "total": len(logs), "filtered_level": level}
