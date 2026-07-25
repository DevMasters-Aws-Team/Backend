# Kiro Monitor Agent - Backend API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12+-blue?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker)
![AWS](https://img.shields.io/badge/AWS-CloudWatch-orange?style=for-the-badge&logo=amazon-aws)

**Generador de logs sinteticos e-commerce + integracion con AWS CloudWatch Logs**

</div>

---

## Quick Start

### Prerequisitos

- Python 3.12 o superior ([descargar](https://www.python.org/downloads/) -- marcar "Add to PATH")
- Poetry (se instala automaticamente en el paso 2)
- Credenciales AWS con acceso a CloudWatch Logs (para envio real de logs)

### 1. Clonar e ir al directorio

```bash
git clone https://github.com/DevMasters-Aws-Team/Backend.git
cd Backend
```

### 2. Instalar dependencias

```bash
python -m pip install poetry
python -m poetry install
```

### 3. Configurar variables de entorno

```bash
copy .env.example .env
```

Editar `.env` con tus credenciales AWS reales:

```
ENVIRONMENT=dev
SERVER_PORT=8000
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=tu_access_key_aqui
AWS_SECRET_ACCESS_KEY=tu_secret_key_aqui
LOG_GROUP_NAME=/kiro/microservices/backend
```

> Las credenciales AWS son necesarias para enviar logs a CloudWatch. Sin ellas el backend funciona pero no envia nada a AWS.

### 4. Levantar el servidor

```bash
python -m poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Verificar que funciona

Abrir en el navegador:

- `http://localhost:8000/api/health` -- debe devolver JSON con status OK
- `http://localhost:8000/docs` -- Swagger UI con todos los endpoints

> **Nota Windows:** Si PowerShell bloquea scripts, ejecutar primero:
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

---

## Arquitectura del flujo de logs

```
Backend (FastAPI)             AWS CloudWatch               Agente (otro repo)
   Genera logs sinteticos  -->  Recibe los logs        -->  Lee y analiza logs
   y los envia cada 5 seg      en /kiro/microservices/     y da respuestas
                               backend
```

---

## Endpoints Disponibles

### Base URL: `http://localhost:8000`

#### Microservicios E-Commerce

| Ruta | Metodo | Descripcion |
|------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/v1/auth/login` | POST | Login de usuario (JWT mock) |
| `/api/v1/biometric/verify` | POST | Verificacion biometrica |
| `/api/v1/products` | GET | Listar productos |
| `/api/v1/inventory/reserve` | POST | Reservar inventario |
| `/api/v1/address/validate` | POST | Validar direccion de envio |
| `/api/v1/purchase/checkout` | POST | Checkout de orden |
| `/api/v1/sales/pay` | POST | Procesar pago |
| `/api/v1/notifications/email` | POST | Enviar email de notificacion |

#### Simulador de Trafico

| Ruta | Metodo | Descripcion |
|------|--------|-------------|
| `/api/simulator/start` | POST | Iniciar generador de trafico (5 RPS default) |
| `/api/simulator/stop` | POST | Detener generador de trafico |
| `/api/simulator/status` | GET | Estado del simulador |
| `/api/simulator/generate-burst` | POST | Generar ráfaga de N logs |

#### Chaos Engineering

| Ruta | Metodo | Descripcion |
|------|--------|-------------|
| `/chaos/timeout` | POST | Inyectar timeout de base de datos |
| `/chaos/error500` | POST | Forzar HTTP 500 |

#### Inspector de Logs (in-memory)

| Ruta | Metodo | Descripcion |
|------|--------|-------------|
| `/api/logs` | GET | Consultar logs en memoria |

### Ejemplo: Iniciar trafico simulado

```bash
curl -X POST http://localhost:8000/api/simulator/start
```

### Ejemplo: Generar burst de 100 logs

```bash
curl -X POST http://localhost:8000/api/simulator/generate-burst
```

### Ejemplo: Ver logs en memoria

```bash
curl http://localhost:8000/api/logs
```

---

## Estructura del Proyecto

```
Backend/
├── src/
│   ├── main.py                  # FastAPI app, CORS, startup/shutdown
│   ├── config.py                # Variables de entorno (Pydantic Settings)
│   ├── cloudwatch_client.py     # Cliente CloudWatch (buffer + flush cada 5s)
│   ├── traffic_generator.py     # Generador de trafico sintetico
│   ├── user_faker.py            # Generador de usuarios fake
│   ├── routers/
│   │   ├── health.py            # GET /api/health
│   │   ├── e_commerce.py        # 8 endpoints e-commerce
│   │   ├── chaos.py             # Inyeccion de fallos
│   │   ├── simulator.py         # Control del simulador
│   │   └── logs.py              # Inspector de logs en memoria
│   ├── models/
│   │   ├── domain.py            # Modelos de dominio e-commerce
│   │   └── logs.py              # Modelos de logs estructurados
│   └── utils/
│       └── aws_helpers.py       # Factory de clientes boto3
├── tests/                       # Suite de tests (pytest)
├── pyproject.toml               # Dependencias (Poetry)
├── poetry.lock                  # Versiones lockeadas
├── Dockerfile                   # Container para deploy
├── docker-compose.yml           # Docker Compose
├── apprunner.yaml               # AWS App Runner config
├── Makefile                     # Comandos automatizados
├── .env.example                 # Template de variables de entorno
└── README.md                    # Este archivo
```

---

## Configuracion

### Variables de entorno (`.env`)

| Variable | Descripcion | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Entorno (dev/prod) | `dev` |
| `SERVER_PORT` | Puerto del servidor | `8000` |
| `AWS_REGION` | Region AWS | `us-east-1` |
| `AWS_ACCESS_KEY_ID` | Access key AWS | `mock_key` |
| `AWS_SECRET_ACCESS_KEY` | Secret key AWS | `mock_secret` |
| `LOG_GROUP_NAME` | Nombre del Log Group en CloudWatch | `/kiro/microservices/backend` |

### Flush automatico a CloudWatch

El backend envia logs a CloudWatch automaticamente cada 5 segundos. Al iniciar:

1. Verifica/crea el Log Group en CloudWatch
2. Inicia un background task que hace flush cada 5 segundos
3. Al cerrar el servidor, hace un flush final

---

## Docker

```bash
# Construir imagen
docker build -t kiro-backend:latest .

# Ejecutar
docker run -p 8000:8000 --env-file .env kiro-backend:latest

# O con Docker Compose
docker-compose up -d
```

---

## Tests

```bash
python -m poetry run pytest tests/ -v --cov=src --cov-fail-under=80
```

---

## Comandos Makefile

```bash
make install       # Instalar dependencias
make run           # Levantar servidor en desarrollo (port 8000)
make test          # Correr tests
make lint          # Verificar codigo (ruff + black + mypy)
make format        # Auto-formatear codigo
make docker-build  # Build imagen Docker
make docker-up     # Levantar con Docker Compose
make docker-down   # Detener Docker Compose
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
