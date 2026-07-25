from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field

class UserContext(BaseModel):
    dni: str = Field(..., description="Fictitious DNI")
    full_name: str = Field(..., description="Fictitious full name")
    email: str = Field(..., description="Fictitious email")
    ip_address: str = Field(..., description="Client IP address")

class RequestDetail(BaseModel):
    headers: Dict[str, str] = Field(default_factory=dict)
    query_params: Dict[str, Any] = Field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None

class ResponseDetail(BaseModel):
    body: Optional[Dict[str, Any]] = None

class StructuredLogEvent(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    level: str = Field(..., description="INFO, WARN, ERROR, CRITICAL")
    service: str = Field(..., description="Name of microservice")
    endpoint: str = Field(..., description="HTTP Method and Path")
    status_code: int = Field(..., description="HTTP status code")
    error_type: Optional[str] = None
    message: str = Field(..., description="Log message")
    trace_id: str = Field(..., description="Unique trace identifier")
    duration_ms: float = Field(..., description="Execution duration in milliseconds")
    user_context: Optional[UserContext] = None
    request: Optional[RequestDetail] = None
    response: Optional[ResponseDetail] = None
