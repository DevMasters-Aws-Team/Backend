# Global Steering - Backend (Kiro Monitor Agent)

## Stack Tecnológico
- **Lenguaje:** Python 3.12
- **Framework:** FastAPI 0.110+
- **Gestor de paquetes:** uv + Poetry
- **SDK AWS:** boto3 1.34+
- **Validación:** Pydantic v2
- **HTTP async:** httpx
- **Logging:** structlog (JSON estructurado)
- **Tareas async:** Celery + Redis
- **Servidor:** Uvicorn (ASGI)
- **Contenedores:** Docker + docker-compose

## Convenciones de Código Python

### Estructura de Archivos
```
src/
├── main.py                 # FastAPI app entry point
├── config.py               # Settings con Pydantic BaseSettings
├── cloudwatch_client.py    # Integración CloudWatch
├── log_filter.py           # Filtrado Python ERROR/WARN
├── ticket_resolver.py      # Auto-resolución tickets
├── agents/
│   ├── monitor_agent.py    # Agente de vigilancia
│   ├── diagnostic_agent.py # Agente de diagnóstico
│   └── ticket_agent.py     # Agente de tickets
├── skills/
│   ├── restart_service.py  # Skill: reiniciar ECS task
│   ├── clear_cache.py      # Skill: limpiar caché
│   ├── scale_up.py         # Skill: escalar servicio
│   └── purge_queue.py      # Skill: purgar cola SQS
├── models/
│   ├── metrics.py          # Modelos de métricas
│   ├── alerts.py           # Modelos de alertas
│   └── tickets.py          # Modelos de tickets
├── routers/
│   ├── health.py           # Health check endpoints
│   ├── metrics.py          # Endpoints de métricas
│   ├── alerts.py           # Endpoints de alertas
│   ├── diagnose.py         # Endpoints de diagnóstico
│   └── chaos.py            # Endpoints Chaos Engineering
└── utils/
    ├── aws_helpers.py      # Utilidades AWS
    └── error_classifier.py # Clasificador de errores
```

### Reglas de Código
1. **Type hints obligatorios** en todas las funciones y métodos
2. **Docstrings** en formato Google para clases y funciones públicas
3. **Pydantic BaseModel** para todos los request/response bodies
4. **Manejo de errores** con HTTPException y handlers globales
5. **Logging estructurado** siempre en JSON via structlog
6. **Async/await** para toda operación I/O (AWS SDK, HTTP, DB)
7. **Principio DRY:** reutilizar clientes boto3 mediante dependency injection

### Formato de Logs (Contrato Obligatorio)
Todos los microservicios emiten logs en formato JSON hacia CloudWatch:
```json
{
  "timestamp": "2024-01-01T00:30:00Z",
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

### Manejo de Errores
- HTTP 4xx → Error del cliente, loguear como WARN
- HTTP 5xx → Error del servidor, loguear como ERROR
- Excepciones no controladas → loguear como CRITICAL + alertar

### Testing
- Framework: pytest + pytest-asyncio
- Cobertura mínima: 80%
- Mocks para boto3 con moto library
- Tests de integración para endpoints FastAPI con httpx

### Linting y Formato
- Formatter: black
- Linter: ruff
- Type checker: mypy
- Pre-commit hooks obligatorios

## Principios de Diseño
- **Zero falsos positivos:** Solo actuar sobre métricas reales (HTTP 500, 401, 503, timeouts)
- **Filtrado Python:** Solo procesar logs ERROR y WARN (reducir costos ~80%)
- **Least Privilege IAM:** Cada skill solo tiene los permisos mínimos necesarios
- **Idempotencia:** Toda acción de remediación debe ser idempotente
