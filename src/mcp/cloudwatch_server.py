"""
CloudWatch MCP Server — Backend
================================
Servidor MCP que expone herramientas para que el agente Kiro / Kiro IDE
consulten CloudWatch Logs en tiempo real sin necesidad de código extra.

Usa el protocolo MCP via stdio (compatible con Kiro IDE mcp.json).

Herramientas expuestas:
  - get_recent_errors   → Últimos N logs de nivel ERROR del log group
  - get_logs_by_service → Logs de un servicio específico
  - get_log_stats       → Estadísticas: total, errores, warnings, latencia promedio

Ejecutar manualmente:
    python src/mcp/cloudwatch_server.py

O desde mcp.json de Kiro (automático).
"""

import json
import sys
import os
import time
import boto3
from datetime import datetime, timezone, timedelta
from typing import Any

# --- Configuración ----------------------------------------------------------
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
LOG_GROUP_NAME = os.getenv("LOG_GROUP_NAME", "/kiro/microservices/backend")
LOG_STREAM_NAME = "e-commerce-stream"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")


def _get_cw_client():
    """Retorna un cliente boto3 de CloudWatch Logs."""
    kwargs: dict[str, Any] = {"region_name": AWS_REGION}
    if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        kwargs["aws_access_key_id"] = AWS_ACCESS_KEY_ID
        kwargs["aws_secret_access_key"] = AWS_SECRET_ACCESS_KEY
    return boto3.client("logs", **kwargs)


# --- Herramientas MCP -------------------------------------------------------

def get_recent_errors(limit: int = 20) -> dict:
    """
    Obtiene los últimos N eventos de nivel ERROR del log group del Backend.
    
    Args:
        limit: Número máximo de errores a retornar (default: 20)
    
    Returns:
        dict con lista de errores y estadísticas básicas
    """
    try:
        client = _get_cw_client()
        now_ms = int(time.time() * 1000)
        one_hour_ago_ms = now_ms - (60 * 60 * 1000)

        response = client.filter_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamNames=[LOG_STREAM_NAME],
            filterPattern='{ $.level = "ERROR" }',
            startTime=one_hour_ago_ms,
            endTime=now_ms,
            limit=min(limit, 100),
        )

        events = response.get("events", [])
        errors = []
        for ev in events:
            try:
                data = json.loads(ev["message"])
                errors.append({
                    "timestamp": data.get("timestamp", ""),
                    "service": data.get("service", "unknown"),
                    "endpoint": data.get("endpoint", ""),
                    "status_code": data.get("status_code", 500),
                    "error_type": data.get("error_type", "UnknownError"),
                    "message": data.get("message", ""),
                    "trace_id": data.get("trace_id", ""),
                    "duration_ms": data.get("duration_ms", 0),
                })
            except (json.JSONDecodeError, KeyError):
                continue

        return {
            "tool": "get_recent_errors",
            "log_group": LOG_GROUP_NAME,
            "total_errors_found": len(errors),
            "errors": errors,
        }

    except Exception as exc:
        return {
            "tool": "get_recent_errors",
            "error": str(exc),
            "error_type": type(exc).__name__,
            "log_group": LOG_GROUP_NAME,
            "errors": [],
        }


def get_logs_by_service(service_name: str, level: str = "ERROR", limit: int = 50) -> dict:
    """
    Obtiene logs de un microservicio específico filtrados por nivel.
    
    Args:
        service_name: Nombre del servicio (ej: 'sales-service')
        level: Nivel de log: ERROR, WARN, INFO (default: ERROR)
        limit: Máximo de registros (default: 50)
    
    Returns:
        dict con logs del servicio solicitado
    """
    try:
        client = _get_cw_client()
        now_ms = int(time.time() * 1000)
        two_hours_ago_ms = now_ms - (2 * 60 * 60 * 1000)

        filter_pattern = (
            f'{{ $.service = "{service_name}" && $.level = "{level.upper()}" }}'
        )

        response = client.filter_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamNames=[LOG_STREAM_NAME],
            filterPattern=filter_pattern,
            startTime=two_hours_ago_ms,
            endTime=now_ms,
            limit=min(limit, 100),
        )

        events = response.get("events", [])
        logs = []
        for ev in events:
            try:
                data = json.loads(ev["message"])
                logs.append(data)
            except (json.JSONDecodeError, KeyError):
                continue

        return {
            "tool": "get_logs_by_service",
            "service": service_name,
            "level_filter": level.upper(),
            "log_group": LOG_GROUP_NAME,
            "total_found": len(logs),
            "logs": logs,
        }

    except Exception as exc:
        return {
            "tool": "get_logs_by_service",
            "error": str(exc),
            "error_type": type(exc).__name__,
            "service": service_name,
            "logs": [],
        }


def get_log_stats(minutes: int = 30) -> dict:
    """
    Calcula estadísticas de los logs de los últimos N minutos.
    
    Args:
        minutes: Ventana de tiempo en minutos (default: 30)
    
    Returns:
        dict con conteos por nivel, servicios con más errores, latencia promedio
    """
    try:
        client = _get_cw_client()
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - (minutes * 60 * 1000)

        response = client.filter_log_events(
            logGroupName=LOG_GROUP_NAME,
            logStreamNames=[LOG_STREAM_NAME],
            startTime=start_ms,
            endTime=now_ms,
            limit=500,
        )

        events = response.get("events", [])
        counts = {"INFO": 0, "WARN": 0, "ERROR": 0}
        service_errors: dict[str, int] = {}
        durations: list[float] = []

        for ev in events:
            try:
                data = json.loads(ev["message"])
                level = data.get("level", "INFO")
                counts[level] = counts.get(level, 0) + 1

                if level == "ERROR":
                    svc = data.get("service", "unknown")
                    service_errors[svc] = service_errors.get(svc, 0) + 1

                dur = data.get("duration_ms")
                if dur is not None:
                    durations.append(float(dur))
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        avg_latency = round(sum(durations) / len(durations), 2) if durations else 0
        top_error_services = sorted(
            service_errors.items(), key=lambda x: x[1], reverse=True
        )[:5]

        return {
            "tool": "get_log_stats",
            "window_minutes": minutes,
            "log_group": LOG_GROUP_NAME,
            "total_events": len(events),
            "by_level": counts,
            "avg_latency_ms": avg_latency,
            "top_error_services": [
                {"service": svc, "error_count": cnt}
                for svc, cnt in top_error_services
            ],
        }

    except Exception as exc:
        return {
            "tool": "get_log_stats",
            "error": str(exc),
            "error_type": type(exc).__name__,
            "by_level": {},
        }


# --- Protocolo MCP (stdio JSON-RPC 2.0) ------------------------------------

TOOLS = {
    "get_recent_errors": {
        "description": "Obtiene los últimos errores (level=ERROR) del log group del Backend en CloudWatch",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Número máximo de errores a retornar",
                    "default": 20,
                }
            },
        },
        "fn": get_recent_errors,
    },
    "get_logs_by_service": {
        "description": "Obtiene logs de un microservicio específico filtrados por nivel (ERROR, WARN, INFO)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Nombre del microservicio (ej: sales-service, login-service)",
                },
                "level": {
                    "type": "string",
                    "description": "Nivel de log: ERROR, WARN o INFO",
                    "default": "ERROR",
                },
                "limit": {
                    "type": "integer",
                    "description": "Máximo de registros",
                    "default": 50,
                },
            },
            "required": ["service_name"],
        },
        "fn": get_logs_by_service,
    },
    "get_log_stats": {
        "description": "Estadísticas de logs: conteos por nivel, servicios con más errores, latencia promedio",
        "inputSchema": {
            "type": "object",
            "properties": {
                "minutes": {
                    "type": "integer",
                    "description": "Ventana de tiempo en minutos",
                    "default": 30,
                }
            },
        },
        "fn": get_log_stats,
    },
}


def _send(obj: dict) -> None:
    """Envía una respuesta JSON-RPC al stdout."""
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def _handle(request: dict) -> None:
    """Procesa un mensaje JSON-RPC 2.0 del IDE."""
    method = request.get("method", "")
    req_id = request.get("id")

    # Handshake: initialize
    if method == "initialize":
        _send({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "cloudwatch-logs-mcp",
                    "version": "1.0.0",
                },
            },
        })
        return

    # Lista de herramientas disponibles
    if method == "tools/list":
        tools_list = []
        for name, meta in TOOLS.items():
            tools_list.append({
                "name": name,
                "description": meta["description"],
                "inputSchema": meta["inputSchema"],
            })
        _send({"jsonrpc": "2.0", "id": req_id, "result": {"tools": tools_list}})
        return

    # Ejecución de herramienta
    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})

        if tool_name not in TOOLS:
            _send({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
            })
            return

        try:
            result = TOOLS[tool_name]["fn"](**arguments)
            _send({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": json.dumps(result, indent=2)}]
                },
            })
        except Exception as exc:
            _send({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(exc)},
            })
        return

    # Notificación sin respuesta requerida
    if method == "notifications/initialized":
        return

    # Método desconocido
    if req_id is not None:
        _send({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method '{method}' not found"},
        })


def main() -> None:
    """Bucle principal: lee JSON-RPC desde stdin, responde a stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            _handle(request)
        except json.JSONDecodeError:
            pass


if __name__ == "__main__":
    main()
