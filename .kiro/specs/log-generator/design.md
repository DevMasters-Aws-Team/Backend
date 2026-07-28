# Design — Backend Log Generator & CloudWatch Integration

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│               FastAPI Backend (:8000)                        │
│                                                              │
│  TrafficGenerator ──▶ CloudWatchClient ──▶ AWS CloudWatch   │
│  (5 RPS async)        (buffer + 5s flush)  /kiro/microsvcs  │
│                              │                               │
│                    ERROR detected                            │
│                              ▼                               │
│                    _notify_agent()                           │
│                    (thread daemon)──▶ POST :8001/webhook    │
│                                                              │
│  REST API:                                                   │
│  /api/services  → status dinámico desde logs reales         │
│  /api/logs      → CloudWatch + fallback memoria             │
│  /api/alerts    → lista de alertas activas                  │
│  /api/simulator → control del generador                     │
│  /chaos/*       → inyección de fallos (solo dev)            │
└──────────────────────────────────────────────────────────────┘
```

## Component Design

### CloudWatchClient (`src/cloudwatch_client.py`)
- `_recent_events: deque(maxlen=2000)` — buffer local para fallback
- `_logs_buffer: List[dict]` — cola de eventos para flush a CloudWatch
- `emit_log(event)` → almacena + notifica agente si ERROR
- `flush_to_cloudwatch()` → boto3.put_log_events() (max 100 eventos, ordenados)
- `_notify_agent(event)` → POST webhook en thread daemon

### TrafficGenerator (`src/traffic_generator.py`)
- Genera tráfico via `asyncio.create_task()`
- 8 servicios × endpoints simulados × error_rate configurable
- `generate_burst(count)` → N logs síncronos instantáneos

### MCP Server (`src/mcp/cloudwatch_server.py`)
- Protocolo JSON-RPC 2.0 via stdin/stdout
- Herramientas: `get_recent_errors`, `get_logs_by_service`, `get_log_stats`
- Activado por Kiro IDE via `.kiro/settings/mcp.json`

### Skills (`src/skills/`)
- Código Python invocable por el Agente Carmen vía webhook response
- `registry.py` expone `SKILLS_REGISTRY` + `invoke_skill(name, params)`

## Data Flow

```
1. TrafficGenerator.generate_single_journey_step()
2. CloudWatchClient.emit_log(event)
   ├── Append a _recent_events (fallback local)
   ├── Si ERROR → thread → POST :8001/webhook
   └── Append a _logs_buffer (queue para CloudWatch)
3. Background task (cada 5s): flush_to_cloudwatch()
4. Frontend polling (cada 5s): GET /api/logs
   ├── Cache hit (<5s) → _cached_logs
   ├── CloudWatch OK → filter_log_events()
   └── CloudWatch fail → _recent_events (fallback)
```

## API Response Contracts

### GET /api/services
```json
[{"title": "string", "name": "string", "endpoint": "string",
  "status": "ok|warn|down", "reqs": "string", "latency": "string",
  "bars": [0,0,0,0,0,0,0,0,0,0,0,0], "errorType": "none|warn|danger"}]
```

### GET /api/logs
```json
[{"time": "HH:MM:SS", "timestamp": "ISO8601", "service": "string",
  "method": "GET|POST", "status": 200, "level": "INFO|WARN|ERROR", "msg": "string"}]
```

### Webhook payload → Agente Carmen
```json
{"alarm_name": "kiro-error-{service}", "state": "ALARM", "reason": "{message}",
 "dimensions": {"ServiceName": "{service}"},
 "raw_payload": {"error_type": "string", "status_code": 500, "duration_ms": 3400,
                 "endpoint": "string", "trace_id": "string"}}
```

## AWS Infrastructure

| Recurso | Nombre | Propósito |
|---------|--------|-----------|
| CloudWatch Logs | `/kiro/microservices/backend` | Log group principal |
| Log Stream | `e-commerce-stream` | Stream de eventos del simulador |
| EC2 | Backend server | Runtime de producción (puerto 8000) |
| App Runner | apprunner.yaml | Configuración alternativa de despliegue |
