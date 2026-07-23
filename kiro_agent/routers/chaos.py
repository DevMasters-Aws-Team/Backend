"""Chaos Engineering endpoints - Inyección de fallos para probar al agente."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid

router = APIRouter()


class ChaosRequest(BaseModel):
    service: str = "user-service"
    duration_ms: Optional[int] = 30000


# Registro de fallos inyectados
CHAOS_LOG: list = []


@router.post("/timeout")
async def inject_timeout(req: ChaosRequest):
    """Simula un database timeout en el servicio indicado."""
    event = {
        "chaos_id": str(uuid.uuid4())[:8],
        "type": "timeout",
        "service": req.service,
        "endpoint": "POST /api/users",
        "status_code": 500,
        "error_type": "DatabaseTimeoutError",
        "message": f"Connection timeout after {req.duration_ms}ms - pool exhausted",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "injected": True,
    }
    CHAOS_LOG.append(event)
    return {"status": "injected", "event": event}


@router.post("/error500")
async def inject_error_500(req: ChaosRequest):
    """Fuerza un HTTP 500 en el servicio indicado."""
    event = {
        "chaos_id": str(uuid.uuid4())[:8],
        "type": "error500",
        "service": req.service,
        "endpoint": "GET /api/data",
        "status_code": 500,
        "error_type": "InternalServerError",
        "message": "Forced 500 Internal Server Error via chaos injection",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "injected": True,
    }
    CHAOS_LOG.append(event)
    return {"status": "injected", "event": event}


@router.post("/error503")
async def inject_error_503(req: ChaosRequest):
    """Simula Service Unavailable (503)."""
    event = {
        "chaos_id": str(uuid.uuid4())[:8],
        "type": "error503",
        "service": req.service,
        "endpoint": "ANY /*",
        "status_code": 503,
        "error_type": "ServiceUnavailable",
        "message": f"{req.service} is temporarily unavailable (circuit breaker open)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "injected": True,
    }
    CHAOS_LOG.append(event)
    return {"status": "injected", "event": event}


@router.post("/cascade")
async def inject_cascade(req: ChaosRequest):
    """Simula un fallo en cascada originado en el servicio indicado."""
    affected = ["order-service", "notification-service"]
    events = []
    for svc in [req.service] + affected:
        event = {
            "chaos_id": str(uuid.uuid4())[:8],
            "type": "cascade",
            "service": svc,
            "endpoint": "ALL",
            "status_code": 503,
            "error_type": "CascadeFailure",
            "message": f"Cascade failure propagated from {req.service}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "injected": True,
            "origin": req.service,
        }
        events.append(event)
        CHAOS_LOG.append(event)

    return {"status": "injected", "events": events, "affected_services": len(events)}


@router.get("/history")
async def get_chaos_history():
    """Historial de fallos inyectados."""
    return {"events": CHAOS_LOG, "total": len(CHAOS_LOG)}
