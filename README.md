# Kiro Monitor Agent - Backend API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![AWS](https://img.shields.io/badge/AWS-CloudWatch-orange?style=for-the-badge&logo=amazon-aws)

**API REST: Microservicios mock + Endpoints para Dashboard de Observabilidad**

</div>

---

## 🚀 Quick Start (3 comandos)

### Prerequisitos
- Python 3.11 o superior ([descargar](https://www.python.org/downloads/) — marcar "Add to PATH")

### Levantar el proyecto

```bash
# 1. Clonar e ir al directorio
git clone https://github.com/DevMasters-Aws-Team/Backend.git
cd Backend

# 2. Instalar Poetry + dependencias
python -m pip install poetry
python -m poetry lock
python -m poetry install

# 3. Levantar el servidor
python -m poetry run python -m uvicorn kiro_agent.main:app --host 0.0.0.0 --port 8080 --reload
```

**¡Listo!** Abre http://localhost:8080/docs para la documentación interactiva (Swagger UI).

> **Nota Windows:** Si PowerShell bloquea scripts, ejecuta primero:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## 📡 Endpoints Disponibles

### Base URL: `http://localhost:8080`

| Ruta | Método | Descripción |
|------|--------|-------------|
| `/health` | GET | Health check del servidor |
| `/api/services` | GET | Lista microservicios monitoreados |
| `/api/services/{name}` | GET | Estado de un servicio específico |
| `/api/metrics` | GET | Métricas globales (error rate, latencia, uptime) |
| `/api/metrics/{name}` | GET | Métricas históricas por servicio |
| `/api/alerts` | GET | Alertas activas (filtrable por severity/service) |
| `/api/alerts/{id}` | GET | Detalle de alerta con request/response |
| `/api/logs` | GET | Logs filtrados ERROR/WARN |
| `/api/tickets` | GET | Lista de tickets de incidencia |
| `/api/tickets/{id}` | GET | Detalle de un ticket |
| `/api/tickets/resolve` | POST | Auto-resolver un ticket |
| `/api/knowledge` | GET | Base de conocimiento de errores |
| `/api/knowledge` | POST | Agregar error conocido |
| `/api/diagnose` | POST | Solicitar diagnóstico de un error |
| `/chaos/timeout` | POST | Inyectar database timeout |
| `/chaos/error500` | POST | Forzar HTTP 500 |
| `/chaos/error503` | POST | Simular Service Unavailable |
| `/chaos/cascade` | POST | Fallo en cascada multi-servicio |
| `/chaos/history` | GET | Historial de fallos inyectados |

### Ejemplo: Solicitar diagnóstico
```bash
curl -X POST http://localhost:8080/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{"service": "user-service", "error_type": "TimeoutError", "trace_id": "trace-abc123"}'
```

### Ejemplo: Inyectar fallo (Chaos)
```bash
curl -X POST http://localhost:8080/chaos/timeout \
  -H "Content-Type: application/json" \
  -d '{"service": "payment-service", "duration_ms": 30000}'
```

---

## 🏗️ Estructura del Proyecto

```
Backend/
├── .kiro/steering/              # SDD Specs (definiciones previas al código)
│   ├── global_steering.md       # Convenciones y stack
│   ├── architecture_specs.md    # Endpoints y modelos de datos
│   ├── mcp.md                   # Conectores MCP
│   ├── skills.md                # Skills de remediación
│   ├── hooks.md                 # Hooks de desarrollo y runtime
│   └── powers.md                # Permisos IAM
│
├── kiro_agent/                  # Código fuente
│   ├── main.py                  # FastAPI app + routers
│   ├── config.py                # Variables de entorno (Pydantic Settings)
│   ├── routers/                 # Endpoints organizados por dominio
│   │   ├── health.py
│   │   ├── services.py
│   │   ├── metrics.py
│   │   ├── alerts.py
│   │   ├── logs.py
│   │   ├── tickets.py
│   │   ├── knowledge.py
│   │   ├── diagnose.py
│   │   └── chaos.py
│   └── models/                  # Pydantic schemas
│       └── services.py
│
├── Docs/                        # Documentación técnica
│   ├── GUIA_IMPLEMENTACION_AWS.md
│   ├── KIRO_SPEC_PRESENTATION.md
│   └── SPEC_DRIVEN_DEVELOPMENT_BLUEPRINT.md
│
├── pyproject.toml               # Dependencias (Poetry)
├── Dockerfile                   # Container para deploy
├── Makefile                     # Comandos automatizados
├── .env.example                 # Variables de entorno (template)
└── README.md                    # Este archivo
```

---

## ⚙️ Configuración

Copia `.env.example` a `.env` para personalizar:

```bash
copy .env.example .env
```

| Variable | Descripción | Default |
|----------|-------------|---------|
| `AWS_REGION` | Región AWS | `us-east-1` |
| `ENVIRONMENT` | Entorno (dev/prod) | `dev` |
| `SERVER_PORT` | Puerto del servidor | `8080` |
| `CORS_ORIGINS` | Orígenes permitidos | `localhost:5173,3000` |
| `AGENT_ENDPOINT` | URL del agente Kiro | `http://localhost:8081` |

---

## 🐳 Docker

```bash
# Construir
docker build -t kiro-backend:latest .

# Ejecutar
docker run -p 8080:8080 --env-file .env kiro-backend:latest
```

---

## 🧪 Tests

```bash
python -m poetry run python -m pytest tests/ -v
```

---

## 📋 Comandos Makefile

Si tienes `make` disponible:

```bash
make install      # Instalar dependencias
make dev          # Levantar en desarrollo
make test         # Correr tests
make lint         # Verificar código
make lint-fix     # Corregir linting
make docker-build # Build Docker
make clean        # Limpiar cache
```

---

## 👥 Equipo (DevMasters AWS Team)

<table>
<tr>
<td align="center"><sub><b>Ashley Zifrikc Villanueva</b></sub></td>
<td align="center"><sub><b>Julio Vargas</b></sub></td>
<td align="center"><sub><b>Jennifer Nicole Solis</b></sub></td>
<td align="center"><sub><b>Juan Aulla Solis</b></sub></td>
<td align="center"><sub><b>Jesus</b></sub></td>
</tr>
</table>

---

<div align="center">

**Desarrollado con ❤️ por DevMasters AWS Team**

[![Agent](https://img.shields.io/badge/🔗%20Agent-Repo-blue?style=for-the-badge)](https://github.com/DevMasters-Aws-Team/kiro-sre-Monitor-Agent/)
[![Backend](https://img.shields.io/badge/🔗%20Backend-Repo-green?style=for-the-badge)](https://github.com/DevMasters-Aws-Team/Backend)
[![Frontend](https://img.shields.io/badge/🔗%20Frontend-Repo-61DAFB?style=for-the-badge)](https://github.com/DevMasters-Aws-Team/Frontend)

</div>
