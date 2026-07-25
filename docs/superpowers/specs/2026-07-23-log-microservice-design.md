# Specification: E-Commerce Multi-Microservice Production Log Generator

## Overview
This microservice is dedicated strictly to generating and streaming production-like structured JSON logs for an entire multi-domain e-commerce platform. It simulates real user traffic, request/response payloads, fictitious identities (DNI, names, emails, IPs), and chaos fault scenarios to AWS CloudWatch and stdout without agent orchestration or ticket resolution features.

---

## Technical Stack
- **Language:** Python 3.12
- **Framework:** FastAPI 0.110+
- **Dependency & Package Manager:** `uv` + `Poetry` (`pyproject.toml`)
- **AWS SDK:** `boto3` 1.34+ (CloudWatch Logs & Metrics)
- **Validation & DTOs:** Pydantic v2
- **Structured Logging:** `structlog` (JSON format)
- **Server:** Uvicorn (ASGI)
- **Containerization:** Docker & Docker Compose
- **Automation:** Makefile
- **Testing:** `pytest` + `pytest-asyncio` + `moto`

---

## Simulated Microservice Domains & Endpoints

1. **`login-service`** - POST /api/v1/auth/login
2. **`biometric-service`** - POST /api/v1/biometric/verify
3. **`product-service`** - GET /api/v1/products
4. **`inventory-service`** - POST /api/v1/inventory/reserve
5. **`address-validation-service`** - POST /api/v1/address/validate
6. **`purchase-service`** - POST /api/v1/purchase/checkout
7. **`sales-service`** - POST /api/v1/sales/pay
8. **`email-service`** - POST /api/v1/notifications/email

### Chaos Fault Simulation
- POST /chaos/timeout
- POST /chaos/error500

### Traffic Simulator Engine Controls
- POST /api/simulator/start
- POST /api/simulator/stop
- GET /api/simulator/status
- POST /api/simulator/generate-burst
