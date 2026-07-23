# Skills - Backend (Acciones de Remediación)

## Definición
Las Skills son scripts/funciones Lambda que Kiro ejecuta para auto-remediar incidentes. Cada skill es idempotente y tiene permisos IAM mínimos.

## Skills Implementadas

### 1. restart_service
**Propósito:** Reiniciar un task/servicio de ECS cuando se detecta un fallo irrecuperable.

```python
# skills/restart_service.py
"""
Skill: Reiniciar servicio ECS
Trigger: Error 500 persistente, memory leak, container unhealthy
IAM: ecs:StopTask, ecs:UpdateService
"""

async def execute(params: dict) -> dict:
    """
    Params:
        - cluster: str (nombre del cluster ECS)
        - service: str (nombre del servicio)
        - task_id: str (opcional, task específico)
    Returns:
        - status: str (success/failed)
        - new_task_id: str
        - downtime_ms: int
    """
```

### 2. clear_cache
**Propósito:** Limpiar caché Redis cuando se detectan datos corruptos o stale.

```python
# skills/clear_cache.py
"""
Skill: Limpiar caché Redis
Trigger: Respuestas inconsistentes, data stale detectada
IAM: N/A (conexión directa a Redis)
"""

async def execute(params: dict) -> dict:
    """
    Params:
        - pattern: str (patrón de keys a limpiar, ej: "user-service:*")
        - flush_all: bool (default: False, PELIGROSO)
    Returns:
        - keys_deleted: int
        - status: str
    """
```

### 3. scale_up
**Propósito:** Escalar horizontalmente un servicio cuando hay alta demanda o latencia.

```python
# skills/scale_up.py
"""
Skill: Escalar servicio ECS
Trigger: Latencia P99 > umbral, CPU > 80%, error rate > 5%
IAM: ecs:UpdateService, application-autoscaling:RegisterScalableTarget
"""

async def execute(params: dict) -> dict:
    """
    Params:
        - cluster: str
        - service: str
        - desired_count: int (nuevo número de tasks)
        - max_count: int (límite máximo)
    Returns:
        - previous_count: int
        - new_count: int
        - status: str
    """
```

### 4. purge_queue
**Propósito:** Purgar una cola SQS cuando hay mensajes atascados causando backpressure.

```python
# skills/purge_queue.py
"""
Skill: Purgar cola SQS
Trigger: Queue depth > umbral, mensajes en DLQ creciendo
IAM: sqs:PurgeQueue, sqs:GetQueueAttributes
"""

async def execute(params: dict) -> dict:
    """
    Params:
        - queue_url: str
        - confirm: bool (requerido True para ejecutar)
    Returns:
        - messages_purged: int (aproximado)
        - status: str
    """
```

### 5. rotate_connections
**Propósito:** Rotar el connection pool de base de datos cuando hay timeouts persistentes.

```python
# skills/rotate_connections.py
"""
Skill: Rotar connection pool
Trigger: Database connection timeout repetido
IAM: N/A (operación a nivel aplicación)
"""

async def execute(params: dict) -> dict:
    """
    Params:
        - service: str
        - pool_size: int (nuevo tamaño del pool)
    Returns:
        - old_pool_size: int
        - new_pool_size: int
        - active_connections: int
        - status: str
    """
```

### 6. send_alert
**Propósito:** Enviar notificación al equipo cuando se requiere intervención humana.

```python
# skills/send_alert.py
"""
Skill: Enviar alerta al equipo
Trigger: Error nuevo no conocido, skill fallida, escalamiento
IAM: sns:Publish, ses:SendEmail
"""

async def execute(params: dict) -> dict:
    """
    Params:
        - channel: str (sns|ses|slack)
        - severity: str (critical|high|medium|low)
        - message: str
        - context: dict (error details, diagnosis, suggestions)
        - recipients: List[str] (emails o ARNs)
    Returns:
        - message_id: str
        - status: str
    """
```

## Registro de Skills

```python
# skills/registry.py
SKILLS_REGISTRY = {
    "restart_service": {
        "module": "skills.restart_service",
        "description": "Reiniciar servicio/task ECS",
        "risk_level": "high",
        "requires_confirmation": True,
        "iam_permissions": ["ecs:StopTask", "ecs:UpdateService"]
    },
    "clear_cache": {
        "module": "skills.clear_cache",
        "description": "Limpiar caché Redis",
        "risk_level": "medium",
        "requires_confirmation": False,
        "iam_permissions": []
    },
    "scale_up": {
        "module": "skills.scale_up",
        "description": "Escalar servicio horizontalmente",
        "risk_level": "medium",
        "requires_confirmation": True,
        "iam_permissions": ["ecs:UpdateService"]
    },
    "purge_queue": {
        "module": "skills.purge_queue",
        "description": "Purgar cola SQS",
        "risk_level": "high",
        "requires_confirmation": True,
        "iam_permissions": ["sqs:PurgeQueue"]
    },
    "rotate_connections": {
        "module": "skills.rotate_connections",
        "description": "Rotar connection pool DB",
        "risk_level": "low",
        "requires_confirmation": False,
        "iam_permissions": []
    },
    "send_alert": {
        "module": "skills.send_alert",
        "description": "Enviar notificación al equipo",
        "risk_level": "low",
        "requires_confirmation": False,
        "iam_permissions": ["sns:Publish", "ses:SendEmail"]
    }
}
```

## Flujo de Ejecución de Skills

```
Diagnóstico completo
       │
       ▼
Agente selecciona skill apropiada
       │
       ▼
¿Requiere confirmación? (risk_level: high)
       │
       ├── SÍ → Human-in-the-loop (dashboard/SNS)
       │         └── Confirmación recibida → Ejecutar
       │
       └── NO → Ejecutar directamente
              │
              ▼
       Registrar resultado en DynamoDB
              │
              ▼
       Actualizar ticket (si aplica)
              │
              ▼
       Notificar resultado en dashboard
```
