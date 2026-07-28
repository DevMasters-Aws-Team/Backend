"""
Skill: send_alert
==================
Envía una notificación al equipo via SNS (producción) o log estructurado (dev).
Trigger: error nuevo desconocido, skill fallida, escalamiento a humano.

Risk level: LOW — solo notifica, no modifica infraestructura.
IAM necesario: sns:Publish (solo en producción con SNS real).
"""

import time
import structlog
from src.config import settings

logger = structlog.get_logger()


async def execute(params: dict) -> dict:
    """
    Envía una alerta al equipo de operaciones.

    Params:
        severity (str): critical | high | medium | low
        message (str): Mensaje descriptivo del incidente
        service (str): Servicio afectado
        context (dict, optional): Datos adicionales del error
        channel (str, optional): 'sns' | 'log' (default: 'log' en dev, 'sns' en prod)

    Returns:
        dict con message_id, channel, status
    """
    severity = params.get("severity", "medium").upper()
    message = params.get("message", "Alerta sin descripción")
    service = params.get("service", "unknown-service")
    context = params.get("context", {})
    channel = params.get("channel", "sns" if settings.ENVIRONMENT == "production" else "log")

    logger.info("skill_send_alert_start", severity=severity, service=service, channel=channel)
    start_time = time.time()

    try:
        message_id = f"alert-{int(time.time())}-{service}"

        if channel == "sns":
            from src.utils.aws_helpers import get_boto3_client
            sns = get_boto3_client("sns")

            # En producción necesitas el ARN real del topic
            topic_arn = f"arn:aws:sns:{settings.AWS_REGION}::kiro-alerts-{settings.ENVIRONMENT}"

            alert_payload = {
                "severity": severity,
                "service": service,
                "message": message,
                "context": context,
                "environment": settings.ENVIRONMENT,
            }

            import json
            response = sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps(alert_payload),
                Subject=f"[KIRO {severity}] Incidente en {service}",
                MessageAttributes={
                    "severity": {"DataType": "String", "StringValue": severity},
                    "service": {"DataType": "String", "StringValue": service},
                },
            )
            message_id = response.get("MessageId", message_id)
            logger.info("skill_send_alert_sns", message_id=message_id, severity=severity)

        else:
            # Modo log — visible en consola y CloudWatch
            log_fn = logger.error if severity in ("CRITICAL", "HIGH") else logger.warning
            log_fn(
                "kiro_alert_notification",
                severity=severity,
                service=service,
                message=message,
                context=context,
                message_id=message_id,
            )

        return {
            "skill": "send_alert",
            "status": "success",
            "channel": channel,
            "message_id": message_id,
            "severity": severity,
            "service": service,
            "message": f"Alert sent via {channel}: [{severity}] {message}",
            "duration_ms": round((time.time() - start_time) * 1000, 2),
        }

    except Exception as exc:
        logger.error("skill_send_alert_failed", service=service, error=str(exc))
        return {
            "skill": "send_alert",
            "status": "failed",
            "error": str(exc),
            "error_type": type(exc).__name__,
            "duration_ms": round((time.time() - start_time) * 1000, 2),
        }
