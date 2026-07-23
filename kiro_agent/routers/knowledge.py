"""Knowledge Base endpoints - Errores conocidos y soluciones."""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# Base de conocimiento en memoria
KNOWLEDGE_BASE: List[dict] = [
    {
        "id": "KB-001",
        "error_type": "TimeoutError",
        "service": "user-service",
        "solution": {"action": "restart_service", "params": {"service": "user-service"}},
        "confidence": 0.95,
        "occurrences": 12,
        "description": "Database connection pool exhausted. Restart service to reset connections.",
    },
    {
        "id": "KB-002",
        "error_type": "ConnectionError",
        "service": "payment-service",
        "solution": {"action": "rotate_connections", "params": {"pool_size": 50}},
        "confidence": 0.90,
        "occurrences": 8,
        "description": "Payment gateway intermittent failures. Rotate connection pool.",
    },
    {
        "id": "KB-003",
        "error_type": "MemoryError",
        "service": "order-service",
        "solution": {"action": "scale_up", "params": {"desired_count": 3}},
        "confidence": 0.85,
        "occurrences": 4,
        "description": "Memory pressure causing OOM kills. Scale horizontally.",
    },
]


class KnowledgeEntry(BaseModel):
    error_type: str
    service: str
    solution: dict
    confidence: float
    description: str


@router.get("/knowledge")
async def get_knowledge(
    error_type: Optional[str] = Query(None, description="Filtrar por tipo de error"),
    service: Optional[str] = Query(None, description="Filtrar por servicio"),
):
    """Consulta la base de conocimiento de errores conocidos."""
    results = KNOWLEDGE_BASE

    if error_type:
        results = [k for k in results if k["error_type"] == error_type]
    if service:
        results = [k for k in results if k["service"] == service]

    return {"entries": results, "total": len(results)}


@router.post("/knowledge")
async def add_knowledge(entry: KnowledgeEntry):
    """Agrega un nuevo error conocido a la base."""
    new_entry = {
        "id": f"KB-{len(KNOWLEDGE_BASE) + 1:03d}",
        **entry.model_dump(),
        "occurrences": 1,
    }
    KNOWLEDGE_BASE.append(new_entry)
    return {"status": "created", "entry": new_entry}
