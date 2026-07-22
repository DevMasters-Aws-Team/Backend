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
| Python 3.11 | Lenguaje base |
| FastAPI | Framework Web asíncrono y de alto rendimiento |
| Uvicorn | Servidor ASGI para FastAPI |
| Boto3 (AWS SDK) | Integración directa con AWS CloudWatch |
| Pydantic | Validación de datos y serialización JSON |

### **Dependencias Principales**:
- **fastapi** - API REST
- **uvicorn** - Servidor web
- **boto3** - Envío de logs a AWS
- **pydantic** - Modelado y validación de DTOs
- **pytest** - Framework de pruebas unitarias

----

## 📦 Requisitos Previos

- Python 3.11 o superior
- Pip (Gestor de paquetes)
- Credenciales configuradas de AWS (para emisión de logs a CloudWatch)
- Docker (Opcional, para ejecución en contenedores)

## 🚀 Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/DevMasters-Aws-Team/Backend.git
cd Backend
```

2. Crea y activa un entorno virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Ejecuta la aplicación:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
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
├── 📂 .kiro/                         # Fase de Setup / SDD (Definiciones en Markdown)
│   ├── global_steering.md            # Reglas globales de comportamiento y convenciones
│   ├── mcp.md                        # Definición (Spec) de los conectores MCP que se usarán
│   ├── skills.md                     # Definición (Spec) de las Lambdas/Skills de remediación
│   ├── hooks.md                      # Definición (Spec) de los Git Hooks (ej. pytest pre-commit)
│   ├── powers.md                     # Definición (Spec) de las capacidades integradas con AWS
│   └── architecture_specs.md         # Specs técnicos de la API y sus dependencias
│
├── 📂 .git/hooks/                    # ⚡ Git Hooks (Configurados por la IA en base a hooks.md)
│   └── pre-commit                    # Hook que corre "pytest" automáticamente al guardar
│
├── 📂 src/                           # ⚙️ Código Fuente (Generado en la Fase de Build)
│   ├── 📂 app/                       # API REST Principal (Microservicios en FastAPI)
│   ├── 📂 mcp/                       # Implementación en Python de los MCPs definidos en mcp.md
│   ├── 📂 skills/                    # Implementación en Python de las Skills definidas en skills.md
│   └── 📂 tests/                     # Tests automatizados (disparados por el hook)
│
├── requirements.txt                  # Dependencias de Python
└── Dockerfile                        # Configuración del contenedor
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
pytest

# Correr tests con cobertura
pytest --cov=src
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
