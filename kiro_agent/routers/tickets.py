"""Tickets endpoints - Gestión de tickets de incidencia."""

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timezone
import uuid

router = APIRouter()

# Tickets en memoria (en producción sería DynamoDB)
MOCK_TICKETS: List[dict] = [
    {
        "id": "TKT-001",
        "status": "open",
        "service": "payment-service",
        "error_type": "TimeoutError",
        "message": "Payment gateway timeout on POST /api/payments",
        "severity": "ERROR",
        "created_at": "2026-07-23T10:00:00Z",
        "resolved_at": None,
        "resolved_by": None,
    },
    {
        "id": "TKT-002",
        "status": "auto_resolved",
        "service": "user-service",
        "error_type": "ConnectionError",
        "message": "Database connection pool exhausted",
        "severity": "ERROR",
        "created_at": "2026-07-23T09:30:00Z",
        "resolved_at": "2026-07-23T09:30:28Z",
        "resolved_by": "kiro-agent",
    },
    {
        "id": "TKT-003",
        "status": "escalated",
        "service": "order-service",
        "error_type": "UnknownError",
        "message": "Unexpected null pointer in order validation",
        "severity": "ERROR",
        "created_at": "2026-07-23T08:15:00Z",
        "resolved_at": None,
        "resolved_by": None,
    },
]


class TicketResolveRequest(BaseModel):
    ticket_id: str


@router.get("/tickets")
async def get_tickets(
    status: Optional[str] = Query(None, description="open, auto_resolved, escalated, closed"),
):
    """Lista tickets de incidencia."""
    results = MOCK_TICKETS
    if status:
        results = [t for t in results if t["status"] == status]

    return {
        "tickets": results,
        "total": len(results),
        "open": sum(1 for t in MOCK_TICKETS if t["status"] == "open"),
        "resolved": sum(1 for t in MOCK_TICKETS if t["status"] == "auto_resolved"),
    }


@router.get("/tickets/{ticket_id}")
async def get_ticket_detail(ticket_id: str):
    """Detalle de un ticket."""
    for t in MOCK_TICKETS:
        if t["id"] == ticket_id:
            return t
    return {"error": "Ticket not found"}


@router.post("/tickets/resolve")
async def resolve_ticket(req: TicketResolveRequest):
    """Auto-resolver un ticket (simula que el agente lo resolvió)."""
    for t in MOCK_TICKETS:
        if t["id"] == req.ticket_id:
            t["status"] = "auto_resolved"
            t["resolved_at"] = datetime.now(timezone.utc).isoformat()
            t["resolved_by"] = "kiro-agent"
            return {"status": "resolved", "ticket": t}
    return {"error": "Ticket not found"}
