"""Kiro Monitor Agent - Backend API.

Microservicios mock + API REST para el dashboard de observabilidad.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from kiro_agent.config import settings
from kiro_agent.routers import health, services, metrics, alerts, logs, tickets, knowledge, diagnose, chaos

app = FastAPI(
    title="Kiro Monitor Agent - Backend API",
    description="API REST: Microservicios mock con telemetría + endpoints para dashboard de observabilidad",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(services.router, prefix="/api", tags=["Services"])
app.include_router(metrics.router, prefix="/api", tags=["Metrics"])
app.include_router(alerts.router, prefix="/api", tags=["Alerts"])
app.include_router(logs.router, prefix="/api", tags=["Logs"])
app.include_router(tickets.router, prefix="/api", tags=["Tickets"])
app.include_router(knowledge.router, prefix="/api", tags=["Knowledge Base"])
app.include_router(diagnose.router, prefix="/api", tags=["Diagnose"])
app.include_router(chaos.router, prefix="/chaos", tags=["Chaos Engineering"])
