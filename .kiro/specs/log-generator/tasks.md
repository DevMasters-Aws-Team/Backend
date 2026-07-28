# Tasks — Backend Log Generator & CloudWatch Integration

- [x] **Task 1: FastAPI Core** — `src/main.py`
  - App + CORS middleware + routers registrados
  - Startup: flush loop (5s) + auto-burst loop (3min)
  - Shutdown: flush final

- [x] **Task 2: CloudWatch Client** — `src/cloudwatch_client.py`
  - Buffer + flush cada 5s a `/kiro/microservices/backend`
  - Webhook automático al agente en cada ERROR (thread daemon)
  - Fallback a memoria local si CloudWatch no responde

- [x] **Task 3: Traffic Generator** — `src/traffic_generator.py`
  - 8 microservicios e-commerce simulados
  - `error_rate_percentage` configurable
  - `generate_burst(count)` para demo

- [x] **Task 4: API REST** — `src/routers/`
  - `services.py` — CRUD + estado dinámico desde logs reales
  - `logs.py` — CloudWatch query + cache 5s + fallback
  - `alerts.py` — gestión de alertas
  - `chaos.py` — inyección de fallos (guarda env check)
  - `simulator.py` — start/stop/status/burst
  - `health.py` — health check

- [x] **Task 5: Skills Python** — `src/skills/`
  - `restart_service.py`, `scale_up.py`, `clear_cache.py`
  - `rotate_connections.py`, `send_alert.py`, `registry.py`

- [x] **Task 6: MCP Server** — `src/mcp/cloudwatch_server.py`
  - JSON-RPC 2.0 via stdio
  - `get_recent_errors`, `get_logs_by_service`, `get_log_stats`
  - Registrado en `.kiro/settings/mcp.json`

- [x] **Task 7: Kiro IDE Config**
  - `.kiro/settings/mcp.json` — 2 servidores MCP
  - `.kiro/hooks/*.json` — 5 hooks activos
  - `.kiro/steering/*.md` — 6 documentos de steering
  - `.kiro/specs/log-generator/` — requirements + design + tasks

- [x] **Task 8: Tests** — `tests/` (5 archivos, coverage ≥ 80%)
  - `test_health.py`, `test_e_commerce.py`, `test_simulator.py`
  - `test_logs_inspector.py`, `test_coverage_boost.py`

- [x] **Task 9: Despliegue AWS**
  - `Dockerfile` — Python 3.12-slim
  - `apprunner.yaml` — AWS App Runner
  - `docker-compose.yml` — local
  - Desplegado en EC2 puerto 8000
