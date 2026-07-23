# Kiro Monitoring Agent  SRE - Backend API (Microservicios)

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![AWS](https://img.shields.io/badge/AWS-CloudWatch-orange?style=for-the-badge&logo=amazon-aws)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**API REST de Lógica de Negocio y Generación de Telemetría (JSON) para Agente Kiro**

</div>

---

El **Backend API** es un conjunto de microservicios desarrollados con FastAPI que actúan como el núcleo transaccional del proyecto (ej. simulando pasarelas de pago o inventarios). Su principal objetivo es procesar peticiones y emitir **logs estructurados en JSON** hacia AWS CloudWatch, generando los escenarios (anomalías, timeouts) que el Agente Kiro detectará y remediará.

## 📋 Descripción

Este repositorio contiene la lógica de negocio que el Agente Kiro debe proteger. Para propósitos de la hackathon, este backend expone endpoints que permiten simular tanto operaciones exitosas como fallos críticos en cascada, sirviendo como el entorno de pruebas perfecto para la auto-remediación. Además, incluye la implementación técnica de los **Skills** y conectores **MCP** utilizados por el agente.

La API incluye:

- **Endpoints Transaccionales:** Simulaciones de pagos, gestión de inventario y colas.
- **Inyección de Fallos (Chaos Engineering):** Endpoints diseñados para fallar a propósito (ej. saturar pools de conexiones) para disparar las alarmas de CloudWatch.
- **Skills (Powers):** Lambdas de AWS con scripts de auto-remediación invocados por el Agente SRE.
- **Emisión Estructurada de Logs:** Envío de telemetría en formato JSON requerida por la metodología.

---

## 🛠️ Tecnologías Utilizadas

| Tecnología | Propósito |
|------------|-----------|
| Python 3.12 | Lenguaje base |
| FastAPI 0.110+ | Framework Web asíncrono y de alto rendimiento |
| Uvicorn | Servidor ASGI para FastAPI |
| Poetry | Gestión de dependencias y virtualenvs |
| Boto3 (AWS SDK) | Integración directa con CloudWatch, DynamoDB, SNS, Lambda |
| Pydantic v2 | Validación de datos y serialización JSON |
| structlog | Logging estructurado en formato JSON |
| httpx | Cliente HTTP asíncrono |
| Redis | Cache y cola de tareas |

### **Dependencias Principales**:
- **fastapi** - API REST
- **uvicorn** - Servidor web
- **boto3** - Integración AWS (CloudWatch, DynamoDB, SNS, SES, Lambda)
- **pydantic** - Modelado y validación de DTOs
- **structlog** - Logging JSON estructurado
- **httpx** - HTTP client async
- **pytest** + **pytest-asyncio** - Framework de pruebas
- **ruff** + **black** + **mypy** - Linting y type checking

----

## 📦 Requisitos Previos

- Python 3.12 o superior
- Poetry (Gestor de dependencias) o uv
- Credenciales configuradas de AWS (para CloudWatch, DynamoDB)
- Docker (Opcional, para ejecución en contenedores)
- Redis (para cache/queue local)

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/DevMasters-Aws-Team/Backend.git
cd Backend
```

2. Instala dependencias con Poetry:
```bash
poetry install
```

3. Configura variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus credenciales AWS
```

4. Ejecuta la aplicación:
```bash
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

5. Ejecuta tests:
```bash
poetry run pytest tests/ -v --cov=src
```

---

## ⚙️ Configuración

### Variables de Entorno

La aplicación utiliza variables de entorno (archivo `.env`) para la configuración:

| Variable | Descripción | Valor por Defecto |
|----------|-------------|-------------------|
| `ENVIRONMENT` | Entorno activo (dev/prod) | `dev` |
| `SERVER_PORT` | Puerto del servidor | `8000` |
| `AWS_REGION` | Región de AWS para CloudWatch | `us-east-1` |
| `LOG_GROUP_NAME` | Grupo de Logs en CloudWatch | `/kiro/microservices/backend` |

---

## 📚 Documentación de la API

La API incluye documentación OpenAPI interactiva generada automáticamente por FastAPI.

- **Swagger UI (interactivo con ejemplos):** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI (JSON):** `http://localhost:8000/openapi.json`

---

## 🏗️ Estructura del Proyecto y Metodología (Bootcamp)

Alineados completamente con la metodología **Specs Driven Development (SDD)** de la Hackathon, antes de programar los scripts en Python (Fase de Build), el equipo define el comportamiento de los componentes mediante archivos `.md` (Fase de Setup/Spec) para que la IA (Kiro) sepa exactamente cómo trabajar en modo *Supervised*:

```text
Backend/
├── 📂 .kiro/steering/                # Fase de Setup / SDD (Definiciones en Markdown)
│   ├── global_steering.md            # Reglas globales: convenciones Python, formato logs JSON, testing
│   ├── architecture_specs.md         # Endpoints API + Chaos, modelos DynamoDB, flujo de datos
│   ├── mcp.md                        # Conectores MCP: CloudWatch, AWS Docs, Code Repo, Knowledge DB
│   ├── skills.md                     # Skills de remediación: restart, cache, scale, purge, alert
│   ├── hooks.md                      # Git Hooks (ruff, mypy, pytest) + Agent Hooks (auth, filter, audit)
│   └── powers.md                     # Permisos IAM por skill (Least Privilege + Boundary Policy)
│
├── 📂 src/                           # ⚙️ Código Fuente
│   ├── main.py                       # FastAPI app entry point
│   ├── config.py                     # Pydantic BaseSettings
│   ├── cloudwatch_client.py          # Integración CloudWatch
│   ├── log_filter.py                 # Filtrado Python ERROR/WARN
│   ├── ticket_resolver.py            # Auto-resolución tickets (DynamoDB)
│   ├── 📂 agents/                    # Agentes: monitor, diagnostic, ticket
│   ├── 📂 skills/                    # Scripts de remediación
│   ├── 📂 mcp/                       # Servidores MCP (Python)
│   ├── 📂 models/                    # Pydantic models
│   ├── 📂 routers/                   # FastAPI routers (health, metrics, alerts, chaos)
│   └── 📂 utils/                     # Helpers y clasificadores
│
├── 📂 tests/                         # Tests (pytest + pytest-asyncio)
├── pyproject.toml                    # Poetry dependencies
├── Dockerfile
├── docker-compose.yml
└── Makefile                          # Automatización (install, run, test, lint, docker)
```

---

## 📡 Endpoints Principales

### Base URL
```
http://localhost:8000/api/v1
```

### 1. Operaciones Normales

#### POST `/payments/process`
Procesa un pago simulado exitosamente.

**Request:**
```json
{
  "userId": "usr-8923",
  "amount": 150.50,
  "currency": "USD",
  "paymentMethod": "CREDIT_CARD"
}
```

**Response (200 OK):**
```json
{
  "transactionId": "tx-1234abcd",
  "status": "APPROVED",
  "timestamp": "2026-07-22T10:00:00Z"
}
```

### 2. Inyección de Fallos (Para disparar al Agente Kiro)

#### POST `/chaos/simulate-timeout`
Fuerza un error de *Connection Timeout* para saturar el pool simulado y disparar una alarma en EventBridge.

**Response (503 Service Unavailable):**
```json
{
  "error": "ConnectionTimeout",
  "message": "Connection timeout acquiring connection from pool",
  "traceId": "tr-773a9b1"
}
```
*Nota: Este endpoint emite silenciosamente el payload JSON requerido por Kiro hacia CloudWatch Logs.*

---

## 🔧 Desarrollo y Pruebas (Construir en Equipo + PRs)

El desarrollo en equipo sigue el estándar aprendido:

1. El Agente lee los `.md` en `.kiro/` para interiorizar el contexto.
2. Trabaja en tu rama de `feat/nombre-feature`.
3. Kiro trabajará en modo **Supervised** escribiendo el código en `src/`.
4. Al terminar, el **Git Hook** de pre-commit validará que todos los tests pasen de forma automática.
5. Genera el mensaje de commit con IA, haz *push* y abre un PR describiendo los cambios basados en el spec.

### Comandos manuales:
```bash
# Correr tests
poetry run pytest tests/ -v

# Correr tests con cobertura
poetry run pytest tests/ --cov=src --cov-fail-under=80

# Linting
poetry run ruff check src/
poetry run black --check src/
poetry run mypy src/

# Fix linting
poetry run ruff check src/ --fix
poetry run black src/

# Docker
make docker-up    # Levantar con docker-compose
make docker-down  # Detener
```

---

## 📝 Formato de Logs (Contrato con el Agente)

Para que el Agente Kiro pueda razonar adecuadamente, todas las excepciones generadas por el Backend son capturadas y transformadas a este formato JSON estándar antes de enviarse a CloudWatch:

```json
{
  "incidentId": "INC-0823",
  "timestamp": "2026-07-22T14:32:00Z",
  "serviceName": "payment-gateway-svc",
  "logLevel": "ERROR",
  "message": "Connection timeout acquiring connection from pool",
  "traceId": "tr-773a9b1",
  "metrics": {
    "cpuUsage": "89%",
    "activeConnections": 1500
  }
}
```

---

## 🚀 Despliegue (Docker)

El proyecto incluye un `Dockerfile` para un despliegue rápido y homologado.

```bash
# Construir imagen
docker build -t kiro-backend-mock .

# Ejecutar contenedor
docker run -p 8000:8000 \
  -e AWS_REGION=us-east-1 \
  -e LOG_GROUP_NAME=/kiro/microservices/backend \
  kiro-backend-mock
```

---

## 👥 Equipo (DevMasters AWS Team)

<table>
<tr>
<td align="center" width="150">
<sub><b>Ashley Zifrikc Villanueva</b></sub><br />
<a href="#"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
<a href="#"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" /></a>
</td>
<td align="center" width="150">
<sub><b>Julio Vargas</b></sub><br />
<a href="#"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
<a href="#"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" /></a>
</td>
<td align="center" width="150">
<sub><b>Jennifer Nicole Solis</b></sub><br />
<a href="#"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
<a href="#"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" /></a>
</td>
<td align="center" width="150">
<sub><b>Juan Aulla Solis</b></sub><br />
<a href="#"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
<a href="#"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" /></a>
</td>
<td align="center" width="150">
<sub><b>Jesus</b></sub><br />
<a href="#"><img src="https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white" /></a>
<a href="#"><img src="https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white" /></a>
</td>
</tr>
</table>

---

## 📄 Licencia

Este proyecto es desarrollado para la Hackathon.

---

<div align="center">

**Desarrollado con ❤️ por DevMasters AWS Team**

</div>
