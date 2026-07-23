# Spec-Driven Development (SDD) Blueprint: Caso de Uso Completo

Este documento sirve como la **Especificación Base Completa (SDD Blueprint)** para el Agente de Observabilidad Inteligente de AWS. Detalla el esquema formal, el JSON de ejecución real, y la trazabilidad técnica de cómo el framework **KIRO** traduce una alerta en un plano estructurado ejecutable (Spec).

---

## 1. El Esquema Formal de Especificación (Spec Schema)

En el paradigma de **Spec-Driven Development (SDD)**, cada diagnóstico se modela bajo un contrato JSON que especifica el contexto físico de AWS, las restricciones de coste (Steering) y los pipelines de procesamiento (Hooks).

```json
{
  "$schema": "http://kiro.ai/schemas/observability-spec-v1.json",
  "metadata": {
    "spec_id": "string",
    "version": "string",
    "timestamp": "ISO-8601"
  },
  "intent": {
    "incident_id": "string",
    "trigger_source": "string",
    "target_trace_id": "string"
  },
  "steering_policy": {
    "max_dollars_budget": "float",
    "max_tokens_per_session": "integer",
    "max_cloudwatch_queries": "integer"
  },
  "scope": {
    "target_services": [
      {
        "service_name": "string",
        "aws_log_groups": ["string"],
        "architecture_doc_path": "string"
      }
    ]
  },
  "hooks_pipeline": {
    "pre_processing": ["string"],
    "post_processing": ["string"]
  }
}
```

---

## 2. Ejemplo Base Completo: Incidente "Checkout 504 Gateway Timeout"

A continuación se presenta la instancia real del Spec JSON para diagnosticar el fallo de Checkout y transacciones de Pago que se puede utilizar como base de desarrollo y demostración:

```json
{
  "$schema": "http://kiro.ai/schemas/observability-spec-v1.json",
  "metadata": {
    "spec_id": "SPEC-2026-PAY-901",
    "version": "1.0.0",
    "timestamp": "2026-07-21T01:05:00Z"
  },
  "intent": {
    "incident_id": "INC-88902",
    "trigger_source": "AWS_CLOUDWATCH_ALARM_CHECKOUT_TIMEOUT",
    "target_trace_id": "1-5f3e2e4a-1234567890abcdef12345678"
  },
  "steering_policy": {
    "max_dollars_budget": 2.50,
    "max_tokens_per_session": 150000,
    "max_cloudwatch_queries": 20
  },
  "scope": {
    "target_services": [
      {
        "service_name": "checkout-service",
        "aws_log_groups": [
          "/aws/ecs/production-checkout-service",
          "/aws/lambda/checkout-handler"
        ],
        "architecture_doc_path": "openapi/checkout-service.json"
      },
      {
        "service_name": "payment-service",
        "aws_log_groups": [
          "/aws/ecs/production-payment-service",
          "/aws/lambda/payment-processor"
        ],
        "architecture_doc_path": "openapi/payment-service.json"
      }
    ]
  },
  "hooks_pipeline": {
    "pre_processing": [
      "KiroHooksService.run_sanitization_hook",
      "KiroHooksService.run_enrichment_hook"
    ],
    "post_processing": [
      "KiroHooksService.run_notification_hook"
    ]
  }
}
```

---

## 3. Trazabilidad Técnica de Ejecución (Run Step-by-Step)

Cuando el motor `KiroSpecExecutor` carga la especificación anterior, ejecuta la siguiente secuencia determinista de acciones:

```
[SPEC RUN START] - SPEC-2026-PAY-901
├── Paso 1: Carga de Política de Steering
│   ├── max_dollars_budget = 2.50 USD
│   ├── max_cloudwatch_queries = 20
│   └── Inicializa KiroSteeringGuard
│
├── Paso 2: Ejecución de Hooks de Pre-procesamiento
│   ├── Inyecta metadatos del commit git ("run_enrichment_hook")
│   └── Inicializa los filtros regex compilados para enmascaramiento de PII ("run_sanitization_hook")
│
├── Paso 3: Activación del Servidor MCP AWS X-Ray (SRE Specialist)
│   ├── Invoca get_trace_summaries("1-5f3e2e4a-1234567890abcdef12345678")
│   └── Identifica alta latencia (>5s) en el segmento "payment-service"
│
├── Paso 4: Activación del Servidor MCP CloudWatch (Logs Specialist)
│   ├── Ejecuta consulta optimizada de Insights en "/aws/ecs/production-payment-service"
│   ├── Detecta excepción: "DB Timeout on PAYMENT_SERVICE"
│   └── Filtra credenciales y tarjetas del flujo de logs en memoria
│
├── Paso 5: Activación del Servidor MCP de Documentos RAG (Docs Specialist)
│   ├── Descarga "openapi/payment-service.json" desde el bucket S3 "kiro-o11y-kb-docs"
│   └── Detecta violación de contrato: El timeout límite de diseño es de 5s; el log real reporta 5.2s
│
├── Paso 6: Generación del Reporte RCA (Incident Coordinator)
│   ├── Correlaciona: Latencia en X-Ray + DB Timeout en CloudWatch + Violación de diseño OpenAPI
│   └── Estima el coste de tokens consumido de la API de Bedrock (ej: 0.1800 USD)
│
└── Paso 7: Ejecución de Hooks de Post-procesamiento
    └── Envía alerta asíncrona estructurada a Slack ("run_notification_hook") con el resumen RCA
[SPEC RUN END] - STATUS: RESOLVED
```

---

## 4. Comparación de Contratos: Diseño vs. Realidad

El núcleo del valor técnico de SDD se presenta cuando el **Docs Specialist** compara los contratos estáticos con los resultados dinámicos:

| Elemento del Sistema | Especificado en OpenAPI/ADR (S3) | Comportamiento Real Detectado (MCP) | Estado del Contrato |
| :--- | :--- | :--- | :--- |
| **Timeout Límite** | Máximo 5000ms (5 segundos) | 5200ms (5.2 segundos) | **VIOLADO ❌** |
| **Política de Retries** | Retries exponenciales (Max 3) | 1 solo intento directo sin retry | **VIOLADO ❌** |
| **Esquema de Error** | Objeto JSON estructurado con error_code | Excepción Java cruda "DB Timeout" | **VIOLADO ❌** |
| **Cumplimiento de PII** | Ningún dato sensible en texto plano | Tarjeta y email expuestos en log | **VIOLADO (Mitigado por Hook de KIRO) 🛡️** |

---

## 5. Integración con el Código de la Plantilla

El código Python proporcionado en la plantilla materializa este ciclo de vida completo:

1.  **Ejecutor:** [spec_executor.py](file:///C:/Users/USER/Desktop/Template%20-%20A%20-%20A/template_Agent/kiro_agent/services/spec_executor.py) carga el Spec, dispara la orquestación asíncrona, sanitiza los logs en tránsito y despacha las notificaciones Slack correspondientes.
2.  **Garantías:** [agent.py](file:///C:/Users/USER/Desktop/Template%20-%20A%20-%20A/template_Agent/kiro_agent/agent.py) garantiza que se cumplan las políticas de Steering especificadas en el JSON para cada agente participante.
