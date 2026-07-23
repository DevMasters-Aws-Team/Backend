"""Metrics endpoints - Métricas de CloudWatch para el dashboard."""

from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime, timezone, timedelta
import random

router = APIRouter()


@router.get("/metrics")
async def get_metrics(
    service: Optional[str] = Query(None, description="Filtrar por servicio"),
    period: int = Query(300, description="Período en segundos"),
):
    """Obtiene métricas globales o por servicio."""
    return {
        "error_rate": round(random.uniform(0.1, 3.5), 2),
        "latency_p99_ms": random.randint(80, 600),
        "availability_percent": round(random.uniform(99.0, 99.99), 2),
        "active_alerts": random.randint(0, 5),
        "tickets_open": random.randint(0, 3),
        "services_healthy": 4,
        "services_total": 5,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/metrics/{service_name}")
async def get_service_metrics(
    service_name: str,
    metric: str = Query("error_rate", description="Métrica: error_rate, latency_p99, availability"),
    time_range: str = Query("1h", description="Rango: 1h, 6h, 24h, 7d"),
):
    """Obtiene métricas históricas de un servicio específico."""
    # Generar datos de historia simulados
    points = []
    now = datetime.now(timezone.utc)
    intervals = {"1h": 12, "6h": 24, "24h": 48, "7d": 56}
    num_points = intervals.get(time_range, 12)

    for i in range(num_points):
        ts = now - timedelta(minutes=5 * (num_points - i))
        points.append({
            "timestamp": ts.isoformat(),
            "value": round(random.uniform(0.1, 5.0), 2) if metric == "error_rate"
            else random.randint(50, 500) if metric == "latency_p99"
            else round(random.uniform(99.0, 100.0), 3),
        })

    return {
        "service": service_name,
        "metric": metric,
        "time_range": time_range,
        "data_points": points,
    }
