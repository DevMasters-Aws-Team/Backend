# MCP (Model Context Protocol) - Backend

## Definición
Los MCPs son conectores estandarizados que permiten al agente Kiro interactuar con servicios externos para obtener contexto en tiempo real.

## Conectores MCP del Backend

### 1. CloudWatch MCP
**Propósito:** Consultar logs y métricas de CloudWatch en tiempo real.

```json
{
  "name": "cloudwatch-mcp",
  "description": "Conector para obtener logs y métricas de AWS CloudWatch",
  "endpoints": {
    "get_logs": {
      "description": "Obtener logs filtrados por servicio y severidad",
      "params": {
        "log_group": "string (nombre del log group)",
        "filter_pattern": "string (ERROR|WARN)",
        "start_time": "int (timestamp ms)",
        "end_time": "int (timestamp ms)",
        "limit": "int (max eventos)"
      },
      "returns": "List[LogEvent]"
    },
    "get_metrics": {
      "description": "Obtener métricas de un servicio",
      "params": {
        "namespace": "string (AWS/ECS, Custom/Microservices)",
        "metric_name": "string (ErrorRate, Latency, etc.)",
        "dimensions": "Dict[str, str]",
        "period": "int (segundos)",
        "stat": "string (Average, Sum, Maximum)"
      },
      "returns": "List[MetricDataPoint]"
    },
    "get_alarms": {
      "description": "Obtener estado de alarmas activas",
      "params": {
        "state": "string (ALARM|OK|INSUFFICIENT_DATA)",
        "prefix": "string (filtro por nombre)"
      },
      "returns": "List[AlarmInfo]"
    }
  }
}
```

### 2. AWS Docs MCP
**Propósito:** Consultar documentación de servicios AWS para enriquecer diagnósticos.

```json
{
  "name": "aws-docs-mcp",
  "description": "Conector para consultar documentación AWS y best practices",
  "endpoints": {
    "search_docs": {
      "description": "Buscar en documentación AWS",
      "params": {
        "query": "string (término de búsqueda)",
        "service": "string (ecs, lambda, dynamodb, etc.)"
      },
      "returns": "List[DocResult]"
    },
    "get_best_practices": {
      "description": "Obtener best practices para un servicio",
      "params": {
        "service": "string",
        "topic": "string (scaling, error-handling, etc.)"
      },
      "returns": "BestPracticeGuide"
    }
  }
}
```

### 3. Code Repository MCP
**Propósito:** Leer documentación y código del repositorio para contexto de diagnóstico.

```json
{
  "name": "code-repo-mcp",
  "description": "Conector para leer documentación y código del proyecto",
  "endpoints": {
    "read_file": {
      "description": "Leer contenido de un archivo del repositorio",
      "params": {
        "path": "string (ruta relativa)",
        "branch": "string (default: main)"
      },
      "returns": "FileContent"
    },
    "search_code": {
      "description": "Buscar patrones en el código",
      "params": {
        "pattern": "string (regex)",
        "file_types": "List[string] (.py, .ts, etc.)",
        "max_results": "int"
      },
      "returns": "List[CodeMatch]"
    },
    "get_service_docs": {
      "description": "Obtener README y docs de un microservicio",
      "params": {
        "service_name": "string"
      },
      "returns": "ServiceDocumentation"
    }
  }
}
```

### 4. DynamoDB Knowledge MCP
**Propósito:** Consultar y actualizar la base de conocimiento de errores.

```json
{
  "name": "knowledge-mcp",
  "description": "Conector para la base de conocimiento de errores en DynamoDB",
  "endpoints": {
    "search_known_error": {
      "description": "Buscar si un error es conocido",
      "params": {
        "error_type": "string",
        "service": "string"
      },
      "returns": "Optional[KnownError]"
    },
    "register_solution": {
      "description": "Registrar nueva solución en la base",
      "params": {
        "error_type": "string",
        "service": "string",
        "solution": "Dict",
        "confidence": "float"
      },
      "returns": "KnowledgeEntry"
    },
    "get_similar_errors": {
      "description": "Buscar errores similares por patrón",
      "params": {
        "error_message": "string",
        "threshold": "float (0.0-1.0)"
      },
      "returns": "List[KnownError]"
    }
  }
}
```

## Configuración MCP (mcp.json)

```json
{
  "mcpServers": {
    "cloudwatch-mcp": {
      "command": "python",
      "args": ["src/mcp/cloudwatch_server.py"],
      "env": {
        "AWS_REGION": "us-east-1",
        "LOG_LEVEL": "ERROR"
      }
    },
    "aws-docs-mcp": {
      "command": "uvx",
      "args": ["awslabs.aws-documentation-mcp-server@latest"],
      "env": {
        "FASTMCP_LOG_LEVEL": "ERROR"
      }
    },
    "code-repo-mcp": {
      "command": "python",
      "args": ["src/mcp/code_repo_server.py"],
      "env": {
        "REPO_PATH": "./",
        "BRANCH": "main"
      }
    },
    "knowledge-mcp": {
      "command": "python",
      "args": ["src/mcp/knowledge_server.py"],
      "env": {
        "AWS_REGION": "us-east-1",
        "TABLE_NAME": "KnowledgeTable"
      }
    }
  }
}
```

## Flujo MCP en Diagnóstico

```
Error detectado (HTTP 500)
       │
       ▼
CloudWatch MCP → Obtener logs del servicio afectado
       │
       ▼
Knowledge MCP → ¿Error conocido en la base?
       │
       ├── SÍ → Retornar solución almacenada
       │
       └── NO →
              │
              ▼
       Code Repo MCP → Leer docs del servicio
              │
              ▼
       AWS Docs MCP → Best practices relacionadas
              │
              ▼
       Generar diagnóstico + sugerencia
```
