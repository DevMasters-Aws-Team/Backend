import uuid
from fastapi import APIRouter, HTTPException
from src.models.logs import StructuredLogEvent, RequestDetail, ResponseDetail
from src.user_faker import generate_fake_user
from src.cloudwatch_client import cloudwatch_client

router = APIRouter(prefix="/chaos", tags=["Chaos Engineering"])

@router.post("/timeout")
def simulate_timeout(service: str = "purchase-service"):
    user = generate_fake_user()
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    event = StructuredLogEvent(
        level="ERROR",
        service=service,
        endpoint="POST /api/v1/purchase/checkout",
        status_code=504,
        error_type="DatabaseTimeoutError",
        message="Connection timeout acquiring connection from pool after 30000ms",
        trace_id=trace_id,
        duration_ms=30015.0,
        user_context=user,
        request=RequestDetail(body={"dni": user.dni}),
        response=ResponseDetail(body={"error": "DatabaseTimeoutError"})
    )
    cloudwatch_client.emit_log(event)
    raise HTTPException(status_code=503, detail={"error": "DatabaseTimeoutError", "traceId": trace_id})

@router.post("/error500")
def force_error_500(service: str = "sales-service"):
    user = generate_fake_user()
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    event = StructuredLogEvent(
        level="ERROR",
        service=service,
        endpoint="POST /api/v1/sales/pay",
        status_code=500,
        error_type="InternalServerError",
        message="Unhandled exception in payment processing",
        trace_id=trace_id,
        duration_ms=120.0,
        user_context=user,
        request=RequestDetail(body={"dni": user.dni}),
        response=ResponseDetail(body={"error": "InternalServerError"})
    )
    cloudwatch_client.emit_log(event)
    raise HTTPException(status_code=500, detail={"error": "InternalServerError", "traceId": trace_id})
