"""Logs Router - Endpoint for frontend logs explorer with CloudWatch integration."""

import json
import time
from datetime import datetime, timezone
from typing import List, Optional
import structlog
from fastapi import APIRouter, Query
from src.models.logs import StructuredLogEvent
from src.config import settings
from src.utils.aws_helpers import get_boto3_client

logger = structlog.get_logger()

router = APIRouter(prefix="/api", tags=["Log Inspector & CloudWatch Query"])

# Cache en memoria para CloudWatch (TTL de 5 segundos)
_cached_logs: List[StructuredLogEvent] = []
_cached_time: float = 0.0


def get_logs_from_cloudwatch(limit: int = 1000) -> List[StructuredLogEvent]:
    """
    Obtiene los logs reales de AWS CloudWatch.
    Tiene un caché de 5 segundos para proteger la API y no saturar.
    Si falla, cae con gracia al buffer de memoria local (fallback).
    """
    global _cached_logs, _cached_time
    now = time.time()

    if _cached_logs and (now - _cached_time < 5.0):
        return _cached_logs

    try:
        client = get_boto3_client("logs")
        
        # Consultamos a CloudWatch
        response = client.filter_log_events(
            logGroupName=settings.LOG_GROUP_NAME,
            logStreamNames=["e-commerce-stream"],
            limit=limit
        )
        events = response.get("events", [])
        
        # Ordenamos los eventos descendentemente por su timestamp nativo (el más nuevo primero)
        events = sorted(events, key=lambda e: e.get("timestamp", 0), reverse=True)
        
        parsed_logs = []
        for ev in events:
            try:
                # CloudWatch devuelve el log JSON serializado como string en la propiedad 'message'
                data = json.loads(ev["message"])
                log_event = StructuredLogEvent(**data)
                parsed_logs.append(log_event)
            except Exception:
                # Ignorar si no se puede parsear un log individual (por ejemplo, logs de infraestructura no estructurados)
                pass
                
        _cached_logs = parsed_logs
        _cached_time = now
        return parsed_logs

    except Exception as exc:
        logger.warning(
            "cloudwatch_query_failed",
            error=str(exc),
            error_type=type(exc).__name__,
            detail="Fallo de conexión o falta de permisos en AWS. Cayendo a fallback local en memoria."
        )
        # Fallback a los logs locales acumulados en memoria por el simulador
        from src.cloudwatch_client import cloudwatch_client as cw_client
        return cw_client.get_recent_logs(limit=limit)


def transform_log_for_frontend(log: StructuredLogEvent) -> dict:
    """Transform backend log format to frontend expected format."""
    # Extract method from endpoint (e.g., "POST /api/v1/auth/login" -> "POST")
    method = "GET"
    if log.endpoint:
        parts = log.endpoint.split(" ")
        if len(parts) > 0:
            method = parts[0]

    # Format timestamp to short time (e.g., "16:58:12")
    time_str = "00:00:00"
    try:
        if isinstance(log.timestamp, str):
            # Parseamos la fecha ISO
            dt = datetime.fromisoformat(log.timestamp.replace("Z", "+00:00"))
        else:
            dt = log.timestamp
        
        # Convertir a hora local (o simplemente extraer el tiempo HH:MM:SS)
        # Nota: La visualización del front requiere "HH:MM:SS"
        time_str = dt.strftime("%H:%M:%S")
    except Exception:
        time_str = str(log.timestamp)[11:19] if log.timestamp else "00:00:00"

    return {
        "time": time_str,
        "timestamp": log.timestamp if isinstance(log.timestamp, str) else datetime.now(timezone.utc).isoformat(),
        "service": log.service or "unknown",
        "method": method,
        "status": log.status_code or 200,
        "level": log.level or "INFO",
        "msg": log.message or "No message",
    }


@router.get("/logs")
def query_logs(
    dni: Optional[str] = Query(None, description="Filtrar por DNI ficticio del cliente"),
    trace_id: Optional[str] = Query(None, description="Filtrar por ID de traza de transacción"),
    service: Optional[str] = Query(None, description="Filtrar por nombre de microservicio"),
    level: Optional[str] = Query(None, description="Filtrar por nivel de log (INFO, WARN, ERROR)"),
    limit: int = Query(100, ge=1, le=500, description="Límite de registros a retornar")
):
    """
    Inspecciona y busca logs generados en AWS CloudWatch (con fallback local resiliente).
    Retorna datos en formato estructurado de fácil lectura para el frontend.
    """
    logs = get_logs_from_cloudwatch(limit=1000)
    
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
