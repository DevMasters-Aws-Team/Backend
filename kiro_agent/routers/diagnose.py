"""Diagnose endpoints - Solicita diagnóstico al agente Kiro."""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import random

router = APIRouter()


class DiagnoseRequest(BaseModel):
    service: str
    error_type: Optional[str] = None
    trace_id: Optional[str] = None
    message: Optional[str] = None


@router.post("/diagnose")
async def diagnose_error(req: DiagnoseRequest):
    """Solicita diagnóstico automático de un error.
    
    En producción, esto reenviaría al agente Kiro (repo kiro-agent)
    que usa Bedrock para razonar. Aquí simulamos la respuesta.
    """
    # Simulación de diagnóstico (en prod se llama al agente Kiro)
    known_solutions = {
        "TimeoutError": {
            "root_cause": "Database connection pool exhausted",
            "solution": "Restart connection pool or scale service",
            "action": "restart_service",
            "is_known": True,
            "confidence": 0.95,
        },
        "ConnectionError": {
            "root_cause": "Upstream dependency unreachable",
            "solution": "Rotate connections and verify network",
            "action": "rotate_connections",
            "is_known": True,
            "confidence": 0.88,
        },
    }

    diagnosis = known_solutions.get(req.error_type, {
        "root_cause": "Unknown error - requires manual investigation",
        "solution": "Escalate to engineering team",
        "action": "escalate",
        "is_known": False,
        "confidence": round(random.uniform(0.3, 0.6), 2),
    })

    return {
        "service": req.service,
        "error_type": req.error_type,
        "trace_id": req.trace_id,
        "diagnosis": diagnosis,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "kiro-sre",
    }
