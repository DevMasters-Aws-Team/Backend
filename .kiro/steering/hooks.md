# Hooks - Backend

## Definición
Los Hooks son puntos de extensión que inyectan lógica personalizada en eventos del ciclo de desarrollo y ejecución del agente.

## Git Hooks (Pre-commit)

### 1. Linting & Formato
```json
{
  "name": "Python Lint Check",
  "version": "1.0.0",
  "description": "Ejecuta ruff y black antes de cada commit para asegurar código limpio",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py"]
  },
  "then": {
    "type": "runCommand",
    "command": "poetry run ruff check src/ && poetry run black --check src/"
  }
}
```

### 2. Type Checking
```json
{
  "name": "MyPy Type Check",
  "version": "1.0.0",
  "description": "Verifica tipos estáticos con mypy",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py"]
  },
  "then": {
    "type": "runCommand",
    "command": "poetry run mypy src/ --ignore-missing-imports"
  }
}
```

### 3. Tests Unitarios
```json
{
  "name": "Run Tests",
  "version": "1.0.0",
  "description": "Ejecuta pytest con cobertura mínima del 80%",
  "when": {
    "type": "fileEdited",
    "patterns": ["src/**/*.py", "tests/**/*.py"]
  },
  "then": {
    "type": "runCommand",
    "command": "poetry run pytest tests/ -v --cov=src --cov-fail-under=80"
  }
}
```

## Agent Hooks (Runtime)

### 4. AWS Authentication Hook
```json
{
  "name": "AWS Auth Validation",
  "version": "1.0.0",
  "description": "Valida credenciales AWS antes de operaciones CloudWatch/DynamoDB",
  "when": {
    "type": "preToolUse",
    "toolTypes": [".*boto3.*", ".*aws.*"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Verificar que las credenciales AWS están vigentes y el rol IAM tiene permisos para esta operación. Si las credenciales han expirado, renovar con STS antes de continuar."
  }
}
```

### 5. Log Filter Hook
```json
{
  "name": "Log Severity Filter",
  "version": "1.0.0",
  "description": "Filtra logs para procesar solo ERROR y WARN, descartando INFO/DEBUG",
  "when": {
    "type": "postToolUse",
    "toolTypes": [".*cloudwatch.*", ".*logs.*"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Aplicar filtrado Python: solo procesar logs con severidad ERROR o WARN. Descartar INFO y DEBUG para reducir costos. Agregar campo 'filtered_at' con timestamp UTC."
  }
}
```

### 6. Ticket Integration Hook
```json
{
  "name": "Ticket Auto-Correlation",
  "version": "1.0.0",
  "description": "Al detectar un error, buscar automáticamente en la base de conocimiento",
  "when": {
    "type": "postToolUse",
    "toolTypes": [".*diagnose.*", ".*error.*"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Buscar este error en la base de conocimiento (DynamoDB KnowledgeTable). Si es un error conocido, obtener la solución almacenada y preparar auto-resolución. Si es nuevo, preparar alerta para el equipo con contexto completo."
  }
}
```

### 7. Chaos Engineering Safety Hook
```json
{
  "name": "Chaos Safety Guard",
  "version": "1.0.0",
  "description": "Protección para endpoints de Chaos Engineering - solo en ambiente dev/staging",
  "when": {
    "type": "preToolUse",
    "toolTypes": [".*chaos.*"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "VERIFICAR: Este endpoint de Chaos Engineering solo debe ejecutarse en ambiente development o staging. Confirmar que la variable ENVIRONMENT no es 'production'. Si es producción, DENEGAR la operación inmediatamente."
  }
}
```

### 8. Skill Execution Audit Hook
```json
{
  "name": "Skill Audit Trail",
  "version": "1.0.0",
  "description": "Registrar cada ejecución de skill en el audit log",
  "when": {
    "type": "postToolUse",
    "toolTypes": [".*skill.*", ".*restart.*", ".*scale.*", ".*purge.*"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "Registrar esta ejecución de skill en el audit trail: timestamp, skill ejecutada, parámetros, resultado, usuario/agente que la invocó. Guardar en DynamoDB AuditTable."
  }
}
```

## Resumen de Hooks

| Hook | Tipo | Trigger | Acción |
|------|------|---------|--------|
| Python Lint | fileEdited | *.py | runCommand (ruff + black) |
| MyPy Types | fileEdited | *.py | runCommand (mypy) |
| Run Tests | fileEdited | src/, tests/ | runCommand (pytest) |
| AWS Auth | preToolUse | boto3/aws tools | askAgent (validar creds) |
| Log Filter | postToolUse | cloudwatch/logs | askAgent (filtrar ERROR/WARN) |
| Ticket Correlation | postToolUse | diagnose/error | askAgent (buscar en KB) |
| Chaos Safety | preToolUse | chaos endpoints | askAgent (verificar ambiente) |
| Skill Audit | postToolUse | skill execution | askAgent (audit trail) |
