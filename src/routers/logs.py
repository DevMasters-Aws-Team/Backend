"""Logs Router - Endpoint for frontend logs explorer."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Query
from src.models.logs import StructuredLogEvent
from src.cloudwatch_client import cloudwatch_client

router = APIRouter(prefix="/api", tags=["Log Inspector & Local Search"])


def transform_log_for_frontend(log: StructuredLogEvent) -> dict:
    """Transform backend log format to frontend expected format."""
    # Extract method from endpoint (e.g., "POST /api/v1/sales/pay" -> "POST")
    method = "GET"
    if log.endpoint:
        parts = log.endpoint.split(" ")
        if len(parts) > 0:
            method = parts[0]

    # Format timestamp to short time (e.g., "16:58:12")
    time_str = "00:00:00"
    try:
        if isinstance(log.timestamp, str):
            dt = datetime.fromisoformat(log.timestamp.replace("Z", "+00:00"))
        else:
            dt = log.timestamp
        time_str = dt.strftime("%H:%M:%S")
    except Exception:
        time_str = str(log.timestamp)[:8] if log.timestamp else "00:00:00"

    return {
        "time": time_str,
        "service": log.service or "unknown",
        "method": method,
        "status": log.status_code or 200,
        "level": log.level or "INFO",
        "msg": log.message or "No message",
    }


@router.get("/logs")
def query_local_logs(
    dni: Optional[str] = Query(None, description="Filtrar por DNI ficticio del cliente"),
    trace_id: Optional[str] = Query(None, description="Filtrar por ID de traza de transacción"),
    service: Optional[str] = Query(None, description="Filtrar por nombre de microservicio"),
    level: Optional[str] = Query(None, description="Filtrar por nivel de log (INFO, WARN, ERROR)"),
    limit: int = Query(50, ge=1, le=500, description="Límite de registros a retornar")
):
    """
    Inspecciona y busca logs generados en memoria local sin necesidad de AWS CloudWatch.
    Retorna datos en formato compatible con el frontend.
    """
    logs = cloudwatch_client.get_recent_logs(limit=1000)
    
    filtered = []
    for log in logs:
        if dni and (not log.user_context or log.user_context.dni != dni):
            continue
        if trace_id and log.trace_id != trace_id:
            continue
        if service and log.service != service:
            continue
        if level and log.level != level:
            continue
        filtered.append(log)
        
    # Transform to frontend format
    return [transform_log_for_frontend(log) for log in filtered[:limit]]
