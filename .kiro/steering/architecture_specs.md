# Architecture Specs - Backend

## Diagrama de API

```
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (port 8000)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  /api/health          GET    → Health check                      │
│  /api/services        GET    → Lista microservicios monitoreados │
│  /api/metrics         GET    → Métricas CloudWatch en tiempo real│
│  /api/metrics/{svc}   GET    → Métricas por servicio             │
│  /api/alerts          GET    → Alertas activas (filtrable)       │
│  /api/alerts/{id}     GET    → Detalle de alerta específica      │
│  /api/diagnose        POST   → Diagnóstico automático de error   │
│  /api/tickets         GET    → Lista de tickets                  │
│  /api/tickets/resolve POST   → Auto-resolución de ticket         │
│  /api/logs            GET    → Logs filtrados (ERROR/WARN)       │
│  /api/knowledge       GET    → Base de conocimiento              │
│  /api/knowledge       POST   → Agregar error conocido            │
│                                                                   │
│  --- Chaos Engineering (Simulación de fallos) ---                │
│  /chaos/timeout       POST   → Simular timeout de BD             │
│  /chaos/error500      POST   → Forzar HTTP 500                   │
│  /chaos/error503      POST   → Simular Service Unavailable       │
│  /chaos/memory        POST   → Simular memory leak               │
│  /chaos/cascade       POST   → Simular fallo en cascada          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

```
Microservicios (Mock)
       │
       ▼ (emiten logs JSON)
CloudWatch Logs
       │
       ▼ (MCP Protocol)
FastAPI Backend
       │
       ├── LogFilter (Python) → Solo ERROR/WARN
       ├── CloudWatchClient → Consulta métricas
       ├── TicketResolver → Auto-resolución
       └── Agents → Diagnóstico + Acción
              │
              ▼
       DynamoDB (Knowledge Base + Tickets)
```

## Endpoints Detallados

### Health & Status
| Endpoint | Método | Descripción | Response |
|----------|--------|-------------|----------|
| `/api/health` | GET | Health check del agente | `{status, uptime, version}` |
| `/api/services` | GET | Lista servicios monitoreados | `[{name, status, last_check}]` |

### Métricas
| Endpoint | Método | Params | Descripción |
|----------|--------|--------|-------------|
| `/api/metrics` | GET | `?period=300&namespace=AWS/ECS` | Métricas globales |
| `/api/metrics/{service}` | GET | `?metric=error_rate` | Métricas por servicio |

### Alertas
| Endpoint | Método | Params | Descripción |
|----------|--------|--------|-------------|
| `/api/alerts` | GET | `?severity=ERROR&service=user-svc&limit=50` | Alertas filtradas |
| `/api/alerts/{id}` | GET | — | Detalle con request/response |

### Diagnóstico
| Endpoint | Método | Body | Descripción |
|----------|--------|------|-------------|
| `/api/diagnose` | POST | `{error_id, service, trace_id}` | Diagnóstico automático |

### Tickets
| Endpoint | Método | Body | Descripción |
|----------|--------|------|-------------|
| `/api/tickets` | GET | `?status=open` | Lista tickets |
| `/api/tickets/resolve` | POST | `{ticket_id}` | Auto-resolver ticket conocido |

### Logs
| Endpoint | Método | Params | Descripción |
|----------|--------|--------|-------------|
| `/api/logs` | GET | `?service=user-svc&level=ERROR&hours=1` | Logs filtrados |

### Knowledge Base
| Endpoint | Método | Body | Descripción |
|----------|--------|------|-------------|
| `/api/knowledge` | GET | `?error_type=TimeoutError` | Buscar soluciones conocidas |
| `/api/knowledge` | POST | `{error_type, solution, confidence}` | Registrar solución |

### Chaos Engineering
| Endpoint | Método | Body | Descripción |
|----------|--------|------|-------------|
| `/chaos/timeout` | POST | `{service, duration_ms}` | Simular DB timeout |
| `/chaos/error500` | POST | `{service, endpoint}` | Forzar error 500 |
| `/chaos/error503` | POST | `{service}` | Service unavailable |
| `/chaos/memory` | POST | `{service, mb}` | Memory leak simulado |
| `/chaos/cascade` | POST | `{origin_service}` | Fallo en cascada |

## Dependencias AWS (boto3)

| Servicio | Cliente | Operaciones |
|----------|---------|-------------|
| CloudWatch | `cloudwatch` | get_metric_data, describe_alarms |
| CloudWatch Logs | `logs` | filter_log_events, get_log_events |
| DynamoDB | `dynamodb` | query, put_item, update_item |
| SNS | `sns` | publish (alertas) |
| SES | `ses` | send_email (reportes) |
| Lambda | `lambda` | invoke (skills) |
| ECS | `ecs` | stop_task, update_service (remediación) |

## Modelos de Datos (DynamoDB)

### KnowledgeTable
```json
{
  "errorType": "TimeoutError",           // PK
  "service": "user-service",             // SK
  "solution": {
    "action": "restart_service",
    "params": {"service": "user-service"}
  },
  "confidence": 0.95,
  "occurrences": 12,
  "last_seen": "2024-01-01T00:30:00Z"
}
```

### TicketsTable
```json
{
  "ticketId": "TKT-1234",               // PK
  "status": "auto_resolved",
  "service": "user-service",
  "error_type": "TimeoutError",
  "created_at": "2024-01-01T00:30:00Z",
  "resolved_at": "2024-01-01T00:30:30Z",
  "resolved_by": "kiro-agent",
  "solution": {...}
}
```

### IncidentsTable
```json
{
  "incidentId": "INC-5678",             // PK
  "timestamp": "2024-01-01T00:30:00Z",  // SK
  "service": "user-service",
  "endpoint": "POST /api/users",
  "status_code": 500,
  "error_type": "TimeoutError",
  "trace_id": "abc-123-def-456",
  "diagnosis": "Connection pool exhausted",
  "resolution": "auto_resolved",
  "ticket_id": "TKT-1234"
}
```

## Docker Compose

```yaml
services:
  backend:
    build: .
    ports: ["8000:8000"]
    env: AWS credentials + region
    depends_on: [redis]
  
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
```
