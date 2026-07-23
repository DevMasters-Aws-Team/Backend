# Guía de Implementación de Servicios AWS - Backend

## Estado Actual vs Objetivo

El backend actualmente usa **datos mock en memoria**. Esta guía detalla cómo reemplazar cada mock por la conexión real a AWS, en qué archivo hacerlo y qué credenciales/datos se necesitan.

```
ESTADO ACTUAL (Mock)                    OBJETIVO (AWS Real)
─────────────────────                   ────────────────────
Listas Python en memoria        →       DynamoDB Tables
Datos random de métricas        →       CloudWatch Metrics API
Logs simulados                  →       CloudWatch Logs Insights
Alertas hardcoded               →       CloudWatch Alarms
Diagnóstico simulado            →       Bedrock (vía kiro-agent)
Notificaciones inexistentes     →       SNS/SES
```

---

## 1. Amazon DynamoDB

### Qué reemplaza
- `routers/tickets.py` → variable `MOCK_TICKETS`
- `routers/knowledge.py` → variable `KNOWLEDGE_BASE`
- Historial de incidentes (nuevo)

### Dónde implementar
Crear archivo: `kiro_agent/services/dynamodb_service.py`

### Variables de entorno requeridas (.env)
```env
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=AKIA...         # IAM User o dejar vacío si usa IAM Role en ECS
AWS_SECRET_ACCESS_KEY=...
DYNAMODB_KNOWLEDGE_TABLE=KnowledgeTable
DYNAMODB_TICKETS_TABLE=TicketsTable
DYNAMODB_INCIDENTS_TABLE=IncidentsTable
```

### Tablas a crear en AWS

#### KnowledgeTable
```
Partition Key: errorType (String)
Sort Key: service (String)
Attributes: solution (Map), confidence (Number), occurrences (Number), description (String)
```

#### TicketsTable
```
Partition Key: ticketId (String)
Attributes: status, service, error_type, message, severity, created_at, resolved_at, resolved_by
GSI: status-index (PK: status, SK: created_at) → para filtrar tickets abiertos
```

#### IncidentsTable
```
Partition Key: incidentId (String)
Sort Key: timestamp (String)
Attributes: service, endpoint, status_code, error_type, trace_id, diagnosis, resolution
```

### Código de implementación
```python
# kiro_agent/services/dynamodb_service.py
import boto3
from kiro_agent.config import settings

class DynamoDBService:
    def __init__(self):
        self.resource = boto3.resource("dynamodb", region_name=settings.aws_region)
        self.knowledge = self.resource.Table(settings.dynamodb_knowledge_table)
        self.tickets = self.resource.Table(settings.dynamodb_tickets_table)
        self.incidents = self.resource.Table(settings.dynamodb_incidents_table)

    def get_known_error(self, error_type: str, service: str):
        response = self.knowledge.get_item(
            Key={"errorType": error_type, "service": service}
        )
        return response.get("Item")

    def create_ticket(self, ticket: dict):
        self.tickets.put_item(Item=ticket)

    def update_ticket_status(self, ticket_id: str, status: str, resolved_by: str = None):
        update_expr = "SET #s = :status"
        values = {":status": status}
        if resolved_by:
            update_expr += ", resolvedBy = :rb, resolvedAt = :ra"
            values[":rb"] = resolved_by
            values[":ra"] = datetime.now(timezone.utc).isoformat()
        self.tickets.update_item(
            Key={"ticketId": ticket_id},
            UpdateExpression=update_expr,
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues=values,
        )

    def list_tickets(self, status: str = None):
        if status:
            response = self.tickets.query(
                IndexName="status-index",
                KeyConditionExpression="#s = :status",
                ExpressionAttributeNames={"#s": "status"},
                ExpressionAttributeValues={":status": status},
            )
        else:
            response = self.tickets.scan()
        return response.get("Items", [])
```

### Dónde conectar en los routers
```python
# routers/tickets.py — reemplazar MOCK_TICKETS por:
from kiro_agent.services.dynamodb_service import DynamoDBService
db = DynamoDBService()

@router.get("/tickets")
async def get_tickets(status: Optional[str] = None):
    tickets = db.list_tickets(status)
    return {"tickets": tickets, "total": len(tickets)}
```

---

## 2. Amazon CloudWatch Logs

### Qué reemplaza
- `routers/logs.py` → datos random generados

### Dónde implementar
Crear archivo: `kiro_agent/services/cloudwatch_service.py`

### Variables de entorno requeridas
```env
AWS_REGION=us-east-1
CLOUDWATCH_LOG_GROUP_PREFIX=/ecs/kiro-
```

### Log Groups esperados en AWS
```
/ecs/kiro-user-service
/ecs/kiro-order-service
/ecs/kiro-payment-service
/ecs/kiro-auth-service
/ecs/kiro-notification-service
```

### Código de implementación
```python
# kiro_agent/services/cloudwatch_service.py
import boto3
from datetime import datetime, timezone, timedelta
from kiro_agent.config import settings

class CloudWatchService:
    def __init__(self):
        self.logs_client = boto3.client("logs", region_name=settings.aws_region)
        self.cw_client = boto3.client("cloudwatch", region_name=settings.aws_region)

    def get_filtered_logs(self, service: str, level: str = "ERROR", hours: int = 1, limit: int = 50):
        """Obtiene logs filtrados de CloudWatch Logs."""
        log_group = f"{settings.cloudwatch_log_group_prefix}{service}"
        start_time = int((datetime.now(timezone.utc) - timedelta(hours=hours)).timestamp() * 1000)
        end_time = int(datetime.now(timezone.utc).timestamp() * 1000)

        try:
            response = self.logs_client.filter_log_events(
                logGroupName=log_group,
                startTime=start_time,
                endTime=end_time,
                filterPattern=f'{{ $.level = "{level}" }}',
                limit=limit,
            )
            return response.get("events", [])
        except self.logs_client.exceptions.ResourceNotFoundException:
            return []

    def get_metric_data(self, namespace: str, metric_name: str, dimensions: list, period: int = 300):
        """Obtiene métricas de CloudWatch Metrics."""
        response = self.cw_client.get_metric_data(
            MetricDataQueries=[{
                "Id": "m1",
                "MetricStat": {
                    "Metric": {
                        "Namespace": namespace,
                        "MetricName": metric_name,
                        "Dimensions": dimensions,
                    },
                    "Period": period,
                    "Stat": "Average",
                },
            }],
            StartTime=datetime.now(timezone.utc) - timedelta(hours=1),
            EndTime=datetime.now(timezone.utc),
        )
        return response.get("MetricDataResults", [])

    def get_active_alarms(self, prefix: str = "kiro-"):
        """Obtiene alarmas activas."""
        response = self.cw_client.describe_alarms(
            StateValue="ALARM",
            AlarmNamePrefix=prefix,
        )
        return response.get("MetricAlarms", [])
```

### Dónde conectar en los routers
```python
# routers/logs.py — reemplazar datos random por:
from kiro_agent.services.cloudwatch_service import CloudWatchService
cw = CloudWatchService()

@router.get("/logs")
async def get_logs(service: Optional[str] = None, level: str = "ERROR", hours: int = 1):
    if service:
        logs = cw.get_filtered_logs(service, level, hours)
    else:
        # Consultar todos los servicios
        logs = []
        for svc in ["user-service", "order-service", "payment-service"]:
            logs.extend(cw.get_filtered_logs(svc, level, hours))
    return {"logs": logs, "total": len(logs)}
```

---

## 3. Amazon CloudWatch Metrics & Alarms

### Qué reemplaza
- `routers/metrics.py` → valores random
- `routers/alerts.py` → alertas mock

### Dónde implementar
Mismo archivo: `kiro_agent/services/cloudwatch_service.py` (ya creado arriba)

### Métricas a configurar en AWS

| Namespace | Metric | Dimensión | Uso |
|-----------|--------|-----------|-----|
| `AWS/ApplicationELB` | `HTTPCode_Target_5XX_Count` | TargetGroup | Error rate |
| `AWS/ApplicationELB` | `TargetResponseTime` | TargetGroup | Latencia |
| `AWS/ECS` | `CPUUtilization` | ServiceName | CPU |
| `AWS/ECS` | `MemoryUtilization` | ServiceName | Memoria |
| `Kiro/Microservices` | `ApplicationErrorCount` | ServiceName | Errores app (custom) |

### Alarmas a crear
```
kiro-high-error-rate    → 5XX > 5 en 2 períodos de 60s
kiro-high-latency       → ResponseTime p99 > 2s en 3 períodos
kiro-service-down       → HealthyHostCount < 1 en 1 período
kiro-memory-pressure    → MemoryUtilization > 90% en 2 períodos
```

### Conexión en router de alerts
```python
# routers/alerts.py — reemplazar MOCK_ALERTS por:
from kiro_agent.services.cloudwatch_service import CloudWatchService
cw = CloudWatchService()

@router.get("/alerts")
async def get_alerts():
    alarms = cw.get_active_alarms("kiro-")
    alerts = [
        {
            "id": alarm["AlarmName"],
            "severity": "ERROR",
            "service": alarm.get("Dimensions", [{}])[0].get("Value", "unknown"),
            "message": alarm.get("AlarmDescription", ""),
            "timestamp": alarm["StateUpdatedTimestamp"].isoformat(),
            "status": "active",
        }
        for alarm in alarms
    ]
    return {"alerts": alerts, "total": len(alerts)}
```

---

## 4. Amazon SNS (Notificaciones)

### Qué reemplaza
- Actualmente no hay notificaciones implementadas

### Dónde implementar
Crear archivo: `kiro_agent/services/notification_service.py`

### Variables de entorno requeridas
```env
SNS_ALERTS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:kiro-alerts
SNS_CRITICAL_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:kiro-critical
```

### Recurso a crear en AWS
```
Topic: kiro-alerts          → Suscripciones: email del equipo, Slack webhook
Topic: kiro-critical        → Suscripciones: SMS del on-call, PagerDuty
```

### Código de implementación
```python
# kiro_agent/services/notification_service.py
import boto3
import json
from kiro_agent.config import settings

class NotificationService:
    def __init__(self):
        self.sns = boto3.client("sns", region_name=settings.aws_region)

    def send_alert(self, subject: str, message: dict, critical: bool = False):
        topic_arn = settings.sns_critical_topic_arn if critical else settings.sns_alerts_topic_arn
        self.sns.publish(
            TopicArn=topic_arn,
            Subject=subject[:100],  # SNS limita a 100 chars
            Message=json.dumps(message, indent=2),
        )

    def notify_resolution(self, ticket_id: str, service: str, solution: str):
        self.send_alert(
            subject=f"[RESOLVED] {service} - Ticket {ticket_id}",
            message={
                "status": "auto_resolved",
                "ticket_id": ticket_id,
                "service": service,
                "solution": solution,
                "resolved_by": "kiro-agent",
            },
        )
```

### Dónde conectar
```python
# routers/tickets.py — después de resolver un ticket:
from kiro_agent.services.notification_service import NotificationService
notifier = NotificationService()

@router.post("/tickets/resolve")
async def resolve_ticket(req: TicketResolveRequest):
    # ... resolver ticket en DynamoDB ...
    notifier.notify_resolution(req.ticket_id, ticket["service"], "auto-resolved")
    return {"status": "resolved", "ticket": ticket}
```

---

## 5. Amazon SES (Emails de Reportes)

### Qué reemplaza
- No implementado actualmente

### Dónde implementar
Agregar al archivo: `kiro_agent/services/notification_service.py`

### Variables de entorno requeridas
```env
SES_FROM_EMAIL=kiro-agent@tudominio.com
SES_REPORT_RECIPIENTS=team@tudominio.com,oncall@tudominio.com
```

### Prerequisitos en AWS
1. Verificar dominio o email en SES
2. Si estás en sandbox: verificar también los emails destinatarios
3. Solicitar salir del sandbox para producción

### Código
```python
# Agregar a notification_service.py:
def send_report_email(self, subject: str, html_body: str, recipients: list):
    self.ses = boto3.client("ses", region_name=settings.aws_region)
    self.ses.send_email(
        Source=settings.ses_from_email,
        Destination={"ToAddresses": recipients},
        Message={
            "Subject": {"Data": subject},
            "Body": {"Html": {"Data": html_body}},
        },
    )
```

---

## 6. CloudWatch Log Emission (Microservicios Mock → CloudWatch)

### Qué reemplaza
- Los endpoints de `/chaos/*` actualmente solo guardan eventos en una lista local

### Dónde implementar
Crear archivo: `kiro_agent/services/log_emitter.py`

### Propósito
Cuando se inyecta un fallo via `/chaos/*`, el backend debe **emitir el log JSON a CloudWatch** para que el agente Kiro (repo separado) lo detecte vía EventBridge.

### Variables de entorno
```env
CLOUDWATCH_LOG_GROUP_PREFIX=/ecs/kiro-
```

### Código de implementación
```python
# kiro_agent/services/log_emitter.py
import boto3
import json
import time
from kiro_agent.config import settings

class LogEmitter:
    def __init__(self):
        self.client = boto3.client("logs", region_name=settings.aws_region)

    def emit_error_log(self, service: str, log_entry: dict):
        """Emite un log JSON estructurado a CloudWatch (simula el microservicio)."""
        log_group = f"{settings.cloudwatch_log_group_prefix}{service}"
        log_stream = f"{service}-{time.strftime('%Y-%m-%d')}"

        # Asegurar que el log group y stream existen
        try:
            self.client.create_log_group(logGroupName=log_group)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

        try:
            self.client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
        except self.client.exceptions.ResourceAlreadyExistsException:
            pass

        # Emitir el log
        self.client.put_log_events(
            logGroupName=log_group,
            logStreamName=log_stream,
            logEvents=[{
                "timestamp": int(time.time() * 1000),
                "message": json.dumps(log_entry),
            }],
        )
```

### Dónde conectar
```python
# routers/chaos.py — después de inyectar un fallo:
from kiro_agent.services.log_emitter import LogEmitter
emitter = LogEmitter()

@router.post("/timeout")
async def inject_timeout(req: ChaosRequest):
    event = { ... }  # como ya está
    
    # NUEVO: Emitir a CloudWatch para que el agente lo detecte
    emitter.emit_error_log(req.service, {
        "timestamp": event["timestamp"],
        "level": "ERROR",
        "service": req.service,
        "endpoint": event["endpoint"],
        "status_code": 500,
        "error_type": "DatabaseTimeoutError",
        "message": event["message"],
        "trace_id": f"trace-{event['chaos_id']}",
        "duration_ms": req.duration_ms,
    })
    
    return {"status": "injected", "event": event}
```

---

## 7. Resumen: Orden de Implementación Recomendado

| Prioridad | Servicio | Archivo a crear/modificar | Impacto en Demo |
|-----------|----------|--------------------------|-----------------|
| 🔴 1 | **Log Emitter** (CW Logs) | `services/log_emitter.py` + `routers/chaos.py` | Sin esto el agente no puede detectar nada |
| 🔴 2 | **DynamoDB** | `services/dynamodb_service.py` + tickets/knowledge routers | Persistencia real de tickets y KB |
| 🟡 3 | **CloudWatch Metrics** | `services/cloudwatch_service.py` + metrics router | Dashboard con datos reales |
| 🟡 4 | **CloudWatch Alarms** | `services/cloudwatch_service.py` + alerts router | Alertas reales en dashboard |
| 🟢 5 | **SNS** | `services/notification_service.py` | Notificaciones al equipo |
| 🟢 6 | **SES** | `services/notification_service.py` | Reportes por email |

---

## 8. Permisos IAM Requeridos

El rol IAM del backend (ECS Task Role) necesita estas policies:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "logs:FilterLogEvents",
        "logs:GetLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/ecs/kiro-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "cloudwatch:GetMetricData",
        "cloudwatch:DescribeAlarms",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:Query",
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:Scan"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/KnowledgeTable",
        "arn:aws:dynamodb:*:*:table/TicketsTable",
        "arn:aws:dynamodb:*:*:table/IncidentsTable",
        "arn:aws:dynamodb:*:*:table/*/index/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["sns:Publish"],
      "Resource": "arn:aws:sns:*:*:kiro-*"
    },
    {
      "Effect": "Allow",
      "Action": ["ses:SendEmail"],
      "Resource": "*",
      "Condition": {
        "StringEquals": {"ses:FromAddress": "kiro-agent@tudominio.com"}
      }
    }
  ]
}
```

---

## 9. Variables de Entorno Completas (.env para producción)

```env
# AWS Core
AWS_REGION=us-east-1
# Si corre en ECS con Task Role, NO necesita estas:
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=

# App
ENVIRONMENT=production
SERVER_PORT=8080
LOG_LEVEL=INFO

# CORS
CORS_ORIGINS=https://kiro-dashboard.amplifyapp.com

# CloudWatch
CLOUDWATCH_LOG_GROUP_PREFIX=/ecs/kiro-

# DynamoDB
DYNAMODB_KNOWLEDGE_TABLE=KnowledgeTable
DYNAMODB_TICKETS_TABLE=TicketsTable
DYNAMODB_INCIDENTS_TABLE=IncidentsTable

# SNS
SNS_ALERTS_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:kiro-alerts
SNS_CRITICAL_TOPIC_ARN=arn:aws:sns:us-east-1:ACCOUNT_ID:kiro-critical

# SES
SES_FROM_EMAIL=kiro-agent@tudominio.com
SES_REPORT_RECIPIENTS=team@tudominio.com

# Agent
AGENT_ENDPOINT=http://kiro-agent-service:8081
```

---

## 10. Testing con Mocks (para desarrollo local sin AWS)

Las dependencias dev ya incluyen `moto` para mockear servicios AWS en tests:

```python
# tests/test_dynamodb_service.py
import pytest
from moto import mock_aws
import boto3
from kiro_agent.services.dynamodb_service import DynamoDBService

@mock_aws
def test_create_and_get_ticket():
    # Crear tabla mock
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
    dynamodb.create_table(
        TableName="TicketsTable",
        KeySchema=[{"AttributeName": "ticketId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "ticketId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )
    
    # Test
    service = DynamoDBService()
    service.create_ticket({"ticketId": "TKT-TEST", "status": "open", "service": "user-service"})
    tickets = service.list_tickets()
    assert len(tickets) == 1
    assert tickets[0]["ticketId"] == "TKT-TEST"
```
