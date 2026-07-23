# Global Steering - Backend (Microservicios Mock + API Dashboard)

## Rol del Repositorio
Este backend cumple DOS funciones:
1. **Simular microservicios de negocio** que emiten logs JSON a CloudWatch (el "paciente" que Kiro vigila)
2. **Servir la API REST** que el frontend (dashboard + chat) consume para mostrar métricas, alertas y estado

La inteligencia del agente Kiro (Bedrock, MCP, decisiones) NO vive aquí — vive en el repo `kiro-agent`.

## Stack Tecnológico
- **Lenguaje:** Python 3.11+
- **Framework:** FastAPI 0.110+
- **Gestor de paquetes:** Poetry
- **SDK AWS:** boto3 1.34+
- **Validación:** Pydantic v2 + pydantic-settings
- **HTTP async:** httpx
- **Logging:** structlog (JSON estructurado hacia CloudWatch)
- **Servidor:** Uvicorn (ASGI)
- **Contenedores:** Docker
- **Puerto:** 8080

## Estructura de Carpetas
```
kiro_agent/
├── main.py                     # FastAPI app entry point
├── config.py                   # Settings con Pydantic BaseSettings
├── routers/
│   ├── health.py               # GET /health
│   ├── services.py             # GET /api/services (lista microservicios)
│   ├── metrics.py              # GET /api/metrics (métricas CloudWatch)
│   ├── alerts.py               # GET /api/alerts (alertas activas)
│   ├── logs.py                 # GET /api/logs (logs filtrados ERROR/WARN)
│   ├── tickets.py              # GET/POST /api/tickets (gestión tickets)
│   ├── knowledge.py            # GET/POST /api/knowledge (base conocimiento)
│   ├── diagnose.py             # POST /api/diagnose (pide diagnóstico al agente)
│   └── chaos.py                # POST /chaos/* (inyección de fallos)
├── services/
│   ├── cloudwatch_service.py   # Lectura de métricas y logs de CloudWatch
│   ├── dynamodb_service.py     # CRUD en DynamoDB (tickets, knowledge, incidents)
│   └── mock_services.py        # Simulación de microservicios de negocio
├── models/
│   ├── metrics.py              # Schemas de métricas
│   ├── alerts.py               # Schemas de alertas
│   ├── tickets.py              # Schemas de tickets
│   ├── services.py             # Schemas de servicios
│   └── logs.py                 # Schemas de logs
├── middleware/
│   ├── cors.py                 # CORS config
│   └── logging_middleware.py   # Structured logging middleware
└── utils/
    ├── log_emitter.py          # Emite logs JSON a CloudWatch (simula microservicios)
    └── error_classifier.py     # Clasifica tipos de error
```

## Convenciones de Código
1. **Type hints obligatorios** en funciones públicas
2. **Pydantic BaseModel** para request/response
3. **Async/await** para operaciones I/O
4. **structlog** para logging JSON estructurado
5. **HTTPException** para errores con status codes claros
6. **Dependency injection** para clientes AWS (facilita testing)

## Formato de Logs Emitidos (Contrato)
Todos los microservicios simulados emiten este formato JSON a CloudWatch:
```json
{
  "timestamp": "2026-07-23T14:30:00Z",
  "level": "ERROR",
  "service": "user-service",
  "endpoint": "POST /api/users",
  "status_code": 500,
  "error_type": "DatabaseTimeoutError",
  "message": "Connection pool exhausted after 30s timeout",
  "trace_id": "abc-123-def-456",
  "duration_ms": 30150
}
```

## Principios
- **El backend NO razona ni decide** — solo emite datos y sirve información
- **Zero falsos positivos en simulación** — los Chaos endpoints generan errores reales (500, 503)
- **Logs siempre en JSON** — CloudWatch los indexa correctamente
- **CORS habilitado** para el frontend en localhost:5173 y producción
