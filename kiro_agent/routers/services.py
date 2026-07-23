"""Services endpoints - Estado de microservicios monitoreados."""

from fastapi import APIRouter
from typing import List
from kiro_agent.models.services import ServiceStatus

router = APIRouter()

# Mock de servicios monitoreados
MOCK_SERVICES: List[dict] = [
    {"name": "user-service", "status": "healthy", "uptime_24h": 99.9, "error_rate": 0.1, "latency_p99": 120},
    {"name": "order-service", "status": "healthy", "uptime_24h": 99.7, "error_rate": 0.3, "latency_p99": 250},
    {"name": "payment-service", "status": "healthy", "uptime_24h": 99.5, "error_rate": 0.5, "latency_p99": 400},
    {"name": "auth-service", "status": "healthy", "uptime_24h": 99.99, "error_rate": 0.01, "latency_p99": 50},
    {"name": "notification-service", "status": "healthy", "uptime_24h": 99.8, "error_rate": 0.2, "latency_p99": 180},
]


@router.get("/services", response_model=List[ServiceStatus])
async def get_services():
    """Lista todos los microservicios monitoreados con su estado actual."""
    return MOCK_SERVICES


@router.get("/services/{service_name}", response_model=ServiceStatus)
async def get_service(service_name: str):
    """Obtiene el estado de un microservicio específico."""
    for svc in MOCK_SERVICES:
        if svc["name"] == service_name:
            return svc
    return {"name": service_name, "status": "unknown", "uptime_24h": 0, "error_rate": 0, "latency_p99": 0}
