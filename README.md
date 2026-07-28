# Kiro SRE — Backend API & Log Generator

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)
![AWS CloudWatch](https://img.shields.io/badge/AWS-CloudWatch-FF9900?style=for-the-badge&logo=amazon-aws)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![EC2](https://img.shields.io/badge/AWS-EC2_Deployed-FF9900?style=for-the-badge&logo=amazon-aws)

**Simulador de Microservicios E-Commerce + API REST para el Dashboard Kiro SRE**

*Proyecto Integrador — Hackathon Kiro DevMasters AWS 2026*

</div>

---

## 🎯 ¿Qué hace este Backend?

Este repositorio cumple **dos roles simultáneos**:

1. **Simulador de microservicios** — genera logs JSON estructurados de 8 servicios de e-commerce y los envía a AWS CloudWatch cada 5 segundos. Es el "paciente" que el Agente Carmen vigila.

2. **API REST** — sirve los datos de microservicios, logs y alertas que el Frontend Dashboard consume en tiempo real.

La inteligencia del agente (Bedrock, LangChain, decisiones) **no vive aquí** — vive en el repo `kiro-sre-Monitor-Agent`.

---

## 🏆 Criterios del Hackathon

| Criterio | Implementación | Estado |
|----------|---------------|--------|
| **MCP** | `.kiro/settings/mcp.json`: `aws-docs` (uvx) + `cloudwatch-logs` (Python custom) | ✅ |
| **Skills** | `src/skills/`: 5 skills Python (restart, scale_up, clear_cache, rotate_connections, send_alert) | ✅ |
| **Hooks** | 5 hooks en `.kiro/hooks/`: lint, tests, chaos-guard, aws-check, audit | ✅ |
| **Powers (IAM)** | Políticas Least Privilege documentadas en `.kiro/steering/powers.md` | ✅ |
| **AWS** | Desplegado en EC2 · CloudWatch conectado (`/kiro/microservices/backend`) | ✅ |
| **Git + PRs** | Organización `DevMasters-Aws-Team` · 3 repos · PRs mergeados | ✅ |
| **Spec (Kiro SDD)** | `.kiro/specs/log-generator/` con requirements, design, tasks | ✅ |
| **Steering** | 6 archivos en `.kiro/steering/`: global, arch, mcp, hooks, skills, powers | ✅ |

---

## 🏗️ Arquitectura del Flujo

```
Backend (FastAPI :8000)
        │
        ├── Genera logs sintéticos de 8 microservicios e-commerce
        │   └── auto-burst: 10 logs cada 3 minutos al iniciar
        │
        ├── Flush a CloudWatch cada 5 segundos
        │   └── Log Group: /kiro/microservices/backend
        │
        ├── CUANDO detecta ERROR → webhook POST a Agente Carmen (:8001)
        │   └── Carmen diagnostica con Bedrock → ejecuta skill si aplica
        │
        └── API REST para el Frontend
            ├── GET /api/services  → estado dinámico calculado desde logs reales
            ├── GET /api/logs      → logs de CloudWatch con filtros (+ fallback)
            ├── GET /api/alerts    → alertas activas
            └── POST /chaos/*      → inyección de fallos controlados
```

---

## 📡 API Reference

### Base URL: `http://localhost:8000`

#### Microservicios E-Commerce (simulados)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/v1/auth/login` | POST | Login de usuario (JWT mock) |
| `/api/v1/biometric/verify` | POST | Verificación biométrica |
| `/api/v1/products` | GET | Catálogo de productos |
| `/api/v1/inventory/reserve` | POST | Reservar inventario |
| `/api/v1/address/validate` | POST | Validar dirección de envío |
| `/api/v1/purchase/checkout` | POST | Checkout de orden |
| `/api/v1/sales/pay` | POST | Procesar pago |
| `/api/v1/notifications/email` | POST | Enviar notificación |

#### Gestión de Microservicios (CRUD dinámico)

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/services` | GET | Lista todos los microservicios con métricas calculadas desde logs reales |
| `/api/services` | POST | Agregar nuevo microservicio al monitoreo |
| `/api/services/validate` | POST | Verificar si un endpoint está disponible |
| `/api/services/{name}` | GET | Detalle de un servicio |
| `/api/services/{name}` | PUT | Actualizar configuración |
| `/api/services/{name}` | DELETE | Eliminar (solo servicios agregados por usuario) |

#### Logs & Alertas

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/logs` | GET | Logs de CloudWatch con filtros: `?service=X&level=ERROR&limit=100` |
| `/api/alerts` | GET | Alertas activas |
| `/api/alerts` | POST | Crear nueva alerta |

#### Simulador de Tráfico

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/simulator/start` | POST | Inicia generador (default: 5 RPS, 10% error rate) |
| `/api/simulator/stop` | POST | Detiene el generador |
| `/api/simulator/status` | GET | Estado actual del simulador |
| `/api/simulator/generate-burst` | POST | Genera N logs de forma inmediata |

#### Chaos Engineering

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/chaos/timeout` | POST | Inyecta DatabaseTimeoutError (solo en dev/staging) |
| `/chaos/error500` | POST | Fuerza HTTP 500 (solo en dev/staging) |

---

## 🔌 MCP Servers

Configurados en `.kiro/settings/mcp.json`:

| Servidor | Tipo | Herramientas | Propósito |
|---------|------|-------------|-----------|
| `aws-docs` | uvx (oficial) | `search_documentation`, `read_documentation` | Consultar docs AWS en Kiro IDE |
| `cloudwatch-logs` | Python custom | `get_recent_errors`, `get_logs_by_service`, `get_log_stats` | Consultar logs del Backend desde Kiro IDE |

El servidor Python custom en `src/mcp/cloudwatch_server.py` usa JSON-RPC 2.0 via stdio.

---

## ⚙️ Skills de Remediación

Ubicadas en `src/skills/` — invocadas por el Agente Carmen vía webhook:

| Skill | Qué hace | AWS Service | Risk |
|-------|---------|-------------|------|
| `restart_service` | ECS forceNewDeployment | ECS | medium |
| `scale_up` | Aumenta desired count | ECS | medium |
| `clear_cache` | Limpia buffer en memoria | — | low |
| `rotate_connections` | Resetea sesión boto3 | — | low |
| `send_alert` | Publica en SNS o log | SNS | low |

---

## 🪝 Hooks de Kiro IDE

| Hook | Trigger | Acción |
|------|---------|--------|
| `python-lint-on-save` | `fileEdited *.py` | `ruff check src/ && black --check src/` |
| `run-tests-on-save` | `fileEdited src/**/*.py` | `pytest tests/ --cov=src --cov-fail-under=80` |
| `chaos-safety-guard` | `preToolUse shell` | Bloquea chaos endpoints en producción |
| `aws-credentials-check` | `preToolUse shell` | Verifica que las credenciales no sean mock |
| `skill-audit-trail` | `postToolUse shell` | Registra skill ejecutada en audit log |

---

## 🚀 Quick Start

### Prerrequisitos
- Python 3.12+
- `pip install poetry`
- Credenciales AWS (para CloudWatch real)

### 1. Instalar y levantar

```bash
git clone https://github.com/DevMasters-Aws-Team/Backend.git
cd Backend
python -m pip install poetry
python -m poetry install
cp .env.example .env
# Editar .env con tus credenciales AWS
python -m poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Variables de entorno (`.env`)

| Variable | Descripción | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | `dev` / `production` | `dev` |
| `AWS_REGION` | Región AWS | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Access key AWS | `mock_key` |
| `AWS_SECRET_ACCESS_KEY` | Secret key AWS | `mock_secret` |
| `LOG_GROUP_NAME` | Log Group CloudWatch | `/kiro/microservices/backend` |
| `AGENT_WEBHOOK_URL` | URL del Agente Carmen | `http://localhost:8001/webhook` |

### 3. Verificar funcionamiento

```bash
# Health check
curl http://localhost:8000/api/health

# Ver logs (con fallback si CloudWatch no responde)
curl "http://localhost:8000/api/logs?level=ERROR&limit=5"

# Estado de microservicios
curl http://localhost:8000/api/services

# Iniciar generador de tráfico
curl -X POST http://localhost:8000/api/simulator/start

# Inyectar fallo (Carmen recibirá el webhook)
curl -X POST http://localhost:8000/chaos/timeout

# Swagger UI
open http://localhost:8000/docs
```

---

## 🗂️ Estructura del Proyecto

```
Backend/
├── .kiro/
│   ├── settings/
│   │   └── mcp.json              ← 2 servidores MCP: aws-docs + cloudwatch-logs
│   ├── hooks/
│   │   ├── python-lint-on-save.json
│   │   ├── run-tests-on-save.json
│   │   ├── chaos-safety-guard.json
│   │   ├── aws-credentials-check.json
│   │   └── skill-audit-trail.json
│   ├── steering/
│   │   ├── global_steering.md    ← Rol del repo y convenciones
│   │   ├── architecture_specs.md ← Diagrama de endpoints
│   │   ├── mcp.md                ← Conectores MCP documentados
│   │   ├── hooks.md              ← Hooks documentados
│   │   ├── skills.md             ← Skills documentadas
│   │   └── powers.md             ← Políticas IAM Least Privilege
│   └── specs/
│       └── log-generator/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── src/
│   ├── main.py                   ← FastAPI app + flush loop + auto-burst
│   ├── config.py                 ← Pydantic Settings
│   ├── cloudwatch_client.py      ← Buffer → CloudWatch + webhook a Carmen
│   ├── traffic_generator.py      ← Simulador de tráfico sintético
│   ├── user_faker.py             ← Usuarios ficticios (DNI, email)
│   ├── mcp/
│   │   └── cloudwatch_server.py  ← MCP server Python (JSON-RPC 2.0)
│   ├── routers/
│   │   ├── health.py, e_commerce.py, chaos.py
│   │   ├── simulator.py, logs.py, services.py, alerts.py
│   ├── skills/
│   │   ├── restart_service.py, scale_up.py, clear_cache.py
│   │   ├── rotate_connections.py, send_alert.py, registry.py
│   ├── models/
│   │   ├── domain.py             ← Modelos e-commerce
│   │   └── logs.py               ← StructuredLogEvent
│   └── utils/
│       └── aws_helpers.py        ← Factory de clientes boto3
├── tests/                        ← pytest + moto (5 archivos)
├── docs/superpowers/             ← Documentación de diseño del hackathon
├── Dockerfile                    ← Python 3.12-slim
├── docker-compose.yml
├── apprunner.yaml                ← AWS App Runner config
├── Makefile
├── pyproject.toml                ← Dependencias (Poetry)
└── .env.example
```

---

## 🧾 Formato de Logs Emitidos a CloudWatch

Todos los microservicios simulados emiten este formato JSON estructurado:

```json
{
  "timestamp": "2026-07-27T14:30:00Z",
  "level": "ERROR",
  "service": "sales-service",
  "endpoint": "POST /api/v1/sales/pay",
  "status_code": 500,
  "error_type": "DatabaseTimeoutError",
  "message": "Connection pool exhausted after 3000ms timeout",
  "trace_id": "tr-abc123def456",
  "duration_ms": 3400.0,
  "user_context": {"dni": "77889900", "full_name": "María García", "email": "m@example.com"},
  "request": {"headers": {"user-agent": "SimulatedUser/1.0"}, "body": {"amount": 199.90}},
  "response": {"body": {"status": "ERROR", "trace_id": "tr-abc123def456"}}
}
```

---

## 🔗 Integración con el Ecosistema

```
Backend (:8000)  ──logs JSON──▶  CloudWatch (/kiro/microservices/backend)
       │                                │
       │ ERROR detectado                │ (consultado por Carmen)
       └──webhook POST──▶  Carmen (:8001) ──▶  Bedrock diagnóstico
                                        │
Frontend (:3000) ──GET polling──▶  Backend (:8000)
                                   /api/services, /api/logs, /api/alerts
```

---

## 🧪 Tests

```bash
python -m poetry run pytest tests/ -v --cov=src --cov-fail-under=80
```

---

## 🐳 Docker

```bash
docker build -t kiro-backend:latest .
docker run -p 8000:8000 --env-file .env kiro-backend:latest
# O con Docker Compose:
docker-compose up -d
```

---

## 👥 Equipo DevMasters AWS Team

<table>
<tr>
<td align="center"><sub><b>Ashley Zifrikc Villanueva</b></sub></td>
<td align="center"><sub><b>Julio Vargas</b></sub></td>
<td align="center"><sub><b>Jennifer Nicole Solis</b></sub></td>
<td align="center"><sub><b>Juan Aulla Solis</b></sub></td>
<td align="center"><sub><b>Jesus</b></sub></td>
</tr>
</table>

<div align="center">

**Desarrollado con ❤️ para el Hackathon Kiro DevMasters AWS 2026**

[![Agent](https://img.shields.io/badge/🔗_Agent-Repo-blue?style=for-the-badge)](https://github.com/DevMasters-Aws-Team/kiro-sre-Monitor-Agent/)
[![Backend](https://img.shields.io/badge/🔗_Backend-Repo-green?style=for-the-badge)](https://github.com/DevMasters-Aws-Team/Backend)
[![Frontend](https://img.shields.io/badge/🔗_Frontend-Repo-61DAFB?style=for-the-badge)](https://github.com/DevMasters-Aws-Team/Frontend)

</div>
