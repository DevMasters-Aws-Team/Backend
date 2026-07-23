"""Service models."""

from pydantic import BaseModel
from typing import Optional


class ServiceStatus(BaseModel):
    name: str
    status: str  # healthy, degraded, down
    uptime_24h: float
    error_rate: float
    latency_p99: int
    last_error: Optional[str] = None
