# Powers (IAM Permissions) - Backend

## Definición
Los Powers definen los permisos IAM que cada componente del agente necesita para operar bajo el principio de Least Privilege.

## Roles IAM

### 1. KiroAgentRole (Principal)
**Propósito:** Rol principal del agente para lectura y monitoreo.

```json
{
  "RoleName": "KiroMonitorAgentRole",
  "AssumeRolePolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": ["lambda.amazonaws.com", "ecs-tasks.amazonaws.com"]},
      "Action": "sts:AssumeRole"
    }]
  },
  "Policies": [
    "KiroCloudWatchReadPolicy",
    "KiroDynamoDBPolicy",
    "KiroSNSPublishPolicy"
  ]
}
```

### 2. KiroCloudWatchReadPolicy
**Propósito:** Lectura de logs y métricas (SOLO lectura).

```json
{
  "PolicyName": "KiroCloudWatchReadPolicy",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "logs:FilterLogEvents",
        "logs:GetLogEvents",
        "logs:DescribeLogGroups",
        "logs:DescribeLogStreams",
        "cloudwatch:GetMetricData",
        "cloudwatch:DescribeAlarms",
        "cloudwatch:ListMetrics"
      ],
      "Resource": "arn:aws:logs:*:*:log-group:/ecs/kiro-*"
    }]
  }
}
```

### 3. KiroDynamoDBPolicy
**Propósito:** Leer/escribir en tablas de conocimiento y tickets.

```json
{
  "PolicyName": "KiroDynamoDBPolicy",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [{
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
        "arn:aws:dynamodb:*:*:table/AuditTable"
      ]
    }]
  }
}
```

### 4. KiroSNSPublishPolicy
**Propósito:** Publicar alertas y notificaciones.

```json
{
  "PolicyName": "KiroSNSPublishPolicy",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:*:*:kiro-alerts-*"
    }]
  }
}
```

### 5. KiroRemediationRole (Skills)
**Propósito:** Permisos para skills de remediación (más privilegiado, requiere confirmación).

```json
{
  "RoleName": "KiroRemediationRole",
  "Policies": ["KiroECSRemediationPolicy", "KiroSQSRemediationPolicy"]
}
```

#### KiroECSRemediationPolicy
```json
{
  "PolicyName": "KiroECSRemediationPolicy",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "ecs:StopTask",
        "ecs:UpdateService",
        "ecs:DescribeServices",
        "ecs:DescribeTasks",
        "ecs:ListTasks"
      ],
      "Resource": "arn:aws:ecs:*:*:cluster/kiro-*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    }]
  }
}
```

#### KiroSQSRemediationPolicy
```json
{
  "PolicyName": "KiroSQSRemediationPolicy",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "sqs:PurgeQueue",
        "sqs:GetQueueAttributes",
        "sqs:GetQueueUrl"
      ],
      "Resource": "arn:aws:sqs:*:*:kiro-*"
    }]
  }
}
```

### 6. KiroSESPolicy
**Propósito:** Envío de emails con reportes.

```json
{
  "PolicyName": "KiroSESPolicy",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Action": [
        "ses:SendEmail",
        "ses:SendRawEmail"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "ses:FromAddress": "kiro-agent@yourdomain.com"
        }
      }
    }]
  }
}
```

## Matriz de Permisos por Skill

| Skill | Rol | Acciones IAM | Risk Level | Confirmación |
|-------|-----|--------------|------------|--------------|
| restart_service | Remediation | ecs:StopTask, ecs:UpdateService | HIGH | Sí |
| clear_cache | Agent | N/A (Redis directo) | MEDIUM | No |
| scale_up | Remediation | ecs:UpdateService | MEDIUM | Sí |
| purge_queue | Remediation | sqs:PurgeQueue | HIGH | Sí |
| rotate_connections | Agent | N/A (aplicación) | LOW | No |
| send_alert | Agent | sns:Publish, ses:SendEmail | LOW | No |

## Guardrails de Seguridad

### Reglas de Protección
1. **NUNCA** permitir `*` en Resource (excepto SES con Condition)
2. **SIEMPRE** limitar por región con Condition
3. **SIEMPRE** usar prefijo `kiro-*` en nombres de recursos
4. **Skills de risk HIGH** requieren confirmación humana
5. **Audit Trail** obligatorio para toda operación de remediación
6. **Rotación de credenciales** cada 12 horas via STS

### Boundary Policy
```json
{
  "PolicyName": "KiroPermissionsBoundary",
  "PolicyDocument": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Deny",
        "Action": [
          "iam:*",
          "organizations:*",
          "ec2:TerminateInstances",
          "rds:DeleteDBInstance",
          "dynamodb:DeleteTable",
          "s3:DeleteBucket"
        ],
        "Resource": "*"
      }
    ]
  }
}
```
