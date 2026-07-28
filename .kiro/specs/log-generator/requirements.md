# Requirements — Backend Log Generator & CloudWatch Integration

## Introduction

El Backend cumple dos roles: simular 8 microservicios de e-commerce que emiten logs JSON a AWS CloudWatch, y servir la API REST que el Frontend consume. Cuando detecta un error, notifica automáticamente al Agente Carmen vía webhook para que inicie el diagnóstico con IA.

## Glossary

| Término | Definición |
|---------|-----------|
| Log Group | Contenedor de logs en CloudWatch (`/kiro/microservices/backend`) |
| Flush | Envío en batch de logs en buffer a CloudWatch (cada 5 segundos) |
| Auto-burst | Generación automática de 10 logs al iniciar el servidor |
| RPS | Requests per second del simulador de tráfico |
| Chaos | Inyección deliberada de fallos para probar al agente |
| Webhook | Notificación automática al Agente Carmen cuando hay un ERROR |

## Requirement 1: Generación de Logs Sintéticos

**User Story:** Como equipo SRE, quiero que el Backend genere logs JSON estructurados que simulen tráfico real de e-commerce, para que el agente Carmen tenga datos reales que analizar.

### Acceptance Criteria

1. WHILE el simulador está activo, THE sistema SHALL generar logs a la tasa configurada (default 5 RPS con 10% error rate)
2. WHEN se genera un log, THE sistema SHALL incluir todos los campos del contrato: `timestamp`, `level`, `service`, `endpoint`, `status_code`, `error_type`, `message`, `trace_id`, `duration_ms`, `user_context`
3. THE sistema SHALL generar automáticamente 10 logs cada 3 minutos como auto-burst al iniciar
4. THE logs de error SHALL tener `duration_ms > 2000` para simular timeouts realistas
5. THE simulador SHALL soportar 8 microservicios: login, biometric, product, inventory, address, purchase, sales, email

## Requirement 2: Integración con AWS CloudWatch

**User Story:** Como equipo DevOps, quiero que los logs se envíen a CloudWatch automáticamente para que puedan ser consultados por el agente y el panel de AWS.

### Acceptance Criteria

1. WHEN el Backend inicia, THE sistema SHALL crear el Log Group si no existe
2. WHILE el Backend está corriendo, THE sistema SHALL hacer flush del buffer a CloudWatch cada 5 segundos en background
3. IF el flush a CloudWatch falla, THEN el sistema SHALL continuar operando con fallback a memoria local (NO lanzar excepción)
4. WHEN el Backend recibe SIGTERM, THE sistema SHALL ejecutar un flush final antes de apagarse
5. THE flush SHALL ordenar los eventos por timestamp (requerimiento de CloudWatch)

## Requirement 3: Notificación Automática al Agente

**User Story:** Como agente SRE autónomo, quiero ser notificado inmediatamente cuando el Backend detecte un ERROR, para iniciar el diagnóstico sin demora.

### Acceptance Criteria

1. WHEN se emite un log con `level = "ERROR"`, THE sistema SHALL enviar webhook POST al Agente Carmen en un thread daemon (no bloqueante)
2. THE payload SHALL cumplir el schema `CloudWatchAlert` del agente (campos: `alarm_name`, `state`, `reason`, `dimensions.ServiceName`, `raw_payload`)
3. IF el agente no está disponible, THEN el Backend SHALL continuar normalmente sin propagar la excepción
4. THE notificación SHALL completarse en background para no bloquear el event loop de FastAPI

## Requirement 4: API REST para el Dashboard

**User Story:** Como ingeniero SRE usando el Dashboard, quiero consultar el estado de los microservicios y logs en tiempo real.

### Acceptance Criteria

1. GET `/api/services` SHALL retornar el estado dinámico calculado desde logs reales de CloudWatch (no datos hardcodeados)
2. GET `/api/logs` SHALL soportar filtros por `service`, `level`, `trace_id`, `dni` y `limit`
3. IF CloudWatch no responde, THEN `/api/logs` SHALL retornar logs del buffer local (fallback resiliente)
4. GET `/api/logs` SHALL tener cache de 5 segundos para no saturar CloudWatch
5. POST `/api/services` SHALL validar duplicados antes de crear un nuevo servicio

## Requirement 5: Chaos Engineering

**User Story:** Como ingeniero de resiliencia, quiero inyectar fallos controlados para probar la respuesta del agente Carmen.

### Acceptance Criteria

1. WHERE `ENVIRONMENT = "production"`, THE sistema SHALL rechazar todas las llamadas a `/chaos/*` con HTTP 403
2. POST `/chaos/timeout` SHALL generar logs con `error_type = "DatabaseTimeoutError"` y `duration_ms > 2000`
3. POST `/chaos/error500` SHALL generar logs con `status_code = 500`
4. THE chaos endpoints SHALL notificar al Agente Carmen para cada error generado

## Correctness Properties

- **P1 (No data loss):** Ningún log emitido se pierde — si CloudWatch falla, el buffer local lo retiene
- **P2 (Error rate accuracy):** La proporción real de ERRORs no se desvía más de ±2% del `error_rate_percentage` configurado
- **P3 (Non-blocking webhook):** El webhook al agente NUNCA bloquea el procesamiento de requests del Backend
- **P4 (Chaos isolation):** Los endpoints de chaos nunca ejecutan en ambiente `production`
