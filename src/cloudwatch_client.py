import os
import time
import json
import threading
import structlog
from collections import deque
from typing import List, Dict, Any
from src.config import settings
from src.utils.aws_helpers import get_boto3_client
from src.models.logs import StructuredLogEvent

logger = structlog.get_logger()

# URL del agente Carmen para notificación automática de errores
AGENT_WEBHOOK_URL = os.getenv("AGENT_WEBHOOK_URL", "http://localhost:8001/webhook")


class CloudWatchClient:
    """
    AWS CloudWatch Logs Integration Client.
    Emits structured JSON log events to CloudWatch Logs group and maintains
    an in-memory buffer for local telemetry inspection.

    Cuando detecta un log de nivel ERROR, notifica automáticamente al agente
    Carmen (webhook) para que diagnostique la causa raíz con Bedrock.
    """
    def __init__(self) -> None:
        self.log_group_name = settings.LOG_GROUP_NAME
        self.log_stream_name = "e-commerce-stream"
        self._logs_buffer: List[Dict[str, Any]] = []
        self._recent_events: deque = deque(maxlen=2000)
        self._stream_ready = False

    def emit_log(self, event: StructuredLogEvent) -> None:
        """Logs structured JSON to stdout, stores in local memory buffer, and queues for CloudWatch."""
        log_dict = event.model_dump()
        self._recent_events.appendleft(event)
        
        if event.level == "ERROR":
            logger.error("microservice_event", **log_dict)
            # Notificación automática al agente Carmen
            self._notify_agent(event)
        elif event.level == "WARN":
            logger.warning("microservice_event", **log_dict)
        else:
            logger.info("microservice_event", **log_dict)
            
        self._logs_buffer.append({
            'timestamp': int(time.time() * 1000),
            'message': json.dumps(log_dict)
        })

    def _notify_agent(self, event: StructuredLogEvent) -> None:
        """Envía el error al agente Carmen via webhook en un thread background.

        El payload respeta el schema CloudWatchAlert del agente.
        """
        def _send() -> None:
            try:
                import httpx

                timestamp = getattr(event, "timestamp", None)
                if timestamp and hasattr(timestamp, "isoformat"):
                    alert_time = timestamp.isoformat()
                else:
                    alert_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

                service = getattr(event, "service", "unknown")
                error_type = getattr(event, "error_type", None) or "InternalServerError"
                message = getattr(event, "message", "")

                payload = {
                    "alarm_name": f"kiro-error-{service}",
                    "alarm_description": f"Error detectado en {service}",
                    "state": "ALARM",
                    "reason": message,
                    "timestamp": alert_time,
                    "region": settings.AWS_REGION,
                    "namespace": getattr(event, "endpoint", "") or service,
                    "metric_name": "ApplicationErrorCount",
                    "dimensions": {"ServiceName": service},
                    "raw_payload": {
                        "error_type": error_type,
                        "status_code": getattr(event, "status_code", 500),
                        "duration_ms": getattr(event, "duration_ms", 0),
                        "endpoint": getattr(event, "endpoint", ""),
                        "trace_id": getattr(event, "trace_id", ""),
                        "message": message,
                    },
                }

                with httpx.Client(timeout=10) as client:
                    response = client.post(AGENT_WEBHOOK_URL, json=payload)
                    if response.status_code == 200:
                        logger.info("agent_notified", service=service, error_type=error_type)
                    else:
                        logger.warning(
                            "agent_notify_rejected",
                            status=response.status_code,
                            service=service,
                            detail=response.text[:200],
                        )
            except Exception as exc:
                # El backend nunca falla si el agente no está disponible
                logger.debug("agent_notification_failed", error=str(exc))

        threading.Thread(target=_send, daemon=True).start()

    def get_recent_logs(self, limit: int = 1000) -> List[StructuredLogEvent]:
        """Returns recent structured log events stored in local memory."""
        return list(self._recent_events)[:limit]

    def _ensure_log_stream(self, client) -> None:
        """Crea el log stream si no existe (AWS lo requiere antes de escribir)."""
        if self._stream_ready:
            return
        try:
            client.create_log_stream(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
            )
            logger.info("log_stream_created", stream=self.log_stream_name)
        except client.exceptions.ResourceAlreadyExistsException:
            pass
        except Exception as exc:
            logger.warning("log_stream_creation_failed", error=str(exc))
            return
        self._stream_ready = True

    def flush_to_cloudwatch(self) -> int:
        """Sends buffered log events to AWS CloudWatch Logs via boto3."""
        if not self._logs_buffer:
            return 0

        # CloudWatch exige eventos ordenados cronológicamente
        batch = sorted(self._logs_buffer[:100], key=lambda e: e["timestamp"])
        count = len(batch)

        try:
            client = get_boto3_client("logs")
            self._ensure_log_stream(client)
            client.put_log_events(
                logGroupName=self.log_group_name,
                logStreamName=self.log_stream_name,
                logEvents=batch,
            )
            logger.info("cloudwatch_put_ok", events=count, log_group=self.log_group_name)
        except Exception as exc:
            # No rompe el backend, pero ahora el error queda registrado
            logger.error(
                "cloudwatch_put_failed",
                error=str(exc),
                error_type=type(exc).__name__,
                log_group=self.log_group_name,
            )
            count = 0
        finally:
            self._logs_buffer.clear()
        return count

cloudwatch_client = CloudWatchClient()
