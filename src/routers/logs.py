from collections import deque
from typing import List, Optional
from fastapi import APIRouter, Query
from src.models.logs import StructuredLogEvent
from src.cloudwatch_client import cloudwatch_client

router = APIRouter(prefix="/api", tags=["Log Inspector & Local Search"])

@router.get("/logs", response_model=List[StructuredLogEvent])
def query_local_logs(
    dni: Optional[str] = Query(None, description="Filtrar por DNI ficticio del cliente"),
    trace_id: Optional[str] = Query(None, description="Filtrar por ID de traza de transacción"),
    service: Optional[str] = Query(None, description="Filtrar por nombre de microservicio"),
    level: Optional[str] = Query(None, description="Filtrar por nivel de log (INFO, WARN, ERROR)"),
    limit: int = Query(50, ge=1, le=500, description="Límite de registros a retornar")
):
    """
    Inspecciona y busca logs generados en memoria local sin necesidad de AWS CloudWatch.
    Permite rastrear el flujo completo de venta de un cliente buscando por su DNI o trace_id.
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
        
    return filtered[:limit]
