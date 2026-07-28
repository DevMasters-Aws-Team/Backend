"""
Skill: scale_up
================
Escala horizontalmente un servicio ECS aumentando el desired count.
Trigger típico: CPU > 80%, latencia P99 > umbral, error rate > 5%.

Risk level: MEDIUM — requiere confirmación si el incremento es > 2x.
IAM necesario: ecs:UpdateService, ecs:DescribeServices
"""

import time
import structlog

logger = structlog.get_logger()


async def execute(params: dict) -> dict:
    """
    Escala un servicio ECS a un nuevo desired count.

    Params:
        service (str): Nombre del servicio
        cluster (str): Nombre del cluster (default: 'kiro-cluster')
        desired_count (int): Nuevo número de tasks deseados
        max_count (int, optional): Límite máximo permitido (default: 10)

    Returns:
        dict con previous_count, new_count, status
    """
    service = params.get("service", "unknown-service")
    cluster = params.get("cluster", "kiro-cluster")
    desired_count = int(params.get("desired_count", 2))
    max_count = int(params.get("max_count", 10))

    logger.info(
        "skill_scale_up_start",
        service=service,
        cluster=cluster,
        desired_count=desired_count,
    )
    start_time = time.time()

    try:
        from src.utils.aws_helpers import get_boto3_client
        ecs = get_boto3_client("ecs")

        # Obtener el desired count actual
        svc_response = ecs.describe_services(cluster=cluster, services=[service])
        svcs = svc_response.get("services", [])
        if not svcs:
            raise ValueError(f"Service '{service}' not found in cluster '{cluster}'")

        previous_count = svcs[0]["desiredCount"]
        safe_count = min(desired_count, max_count)

        ecs.update_service(cluster=cluster, service=service, desiredCount=safe_count)

        logger.info(
            "skill_scale_up_done",
            service=service,
            previous_count=previous_count,
            new_count=safe_count,
        )

        return {
            "skill": "scale_up",
            "status": "success",
            "service": service,
            "cluster": cluster,
            "previous_count": previous_count,
            "new_count": safe_count,
            "message": f"Service '{service}' scaled from {previous_count} to {safe_count} tasks",
            "duration_ms": round((time.time() - start_time) * 1000, 2),
        }

    except Exception as exc:
        logger.error("skill_scale_up_failed", service=service, error=str(exc))
        return {
            "skill": "scale_up",
            "status": "failed",
            "service": service,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "duration_ms": round((time.time() - start_time) * 1000, 2),
        }
