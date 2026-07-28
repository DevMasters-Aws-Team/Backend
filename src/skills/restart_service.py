"""
Skill: restart_service
=======================
Reinicia un servicio ECS (stop task + ECS lo relanza automáticamente).
En desarrollo local simula el reinicio poniendo el servicio en estado 'restarting'.

Risk level: HIGH — requiere confirmación humana en producción.
IAM necesario: ecs:StopTask, ecs:UpdateService, ecs:DescribeTasks
"""

import time
import structlog
from src.config import settings

logger = structlog.get_logger()


async def execute(params: dict) -> dict:
    """
    Reinicia un task/servicio de ECS.

    Params:
        service (str): Nombre del servicio a reiniciar (ej: 'sales-service')
        cluster (str): Nombre del cluster ECS (default: 'kiro-cluster')
        task_id (str, optional): ARN del task específico a parar

    Returns:
        dict con status, mensaje, tiempo de ejecución
    """
    service = params.get("service", "unknown-service")
    cluster = params.get("cluster", "kiro-cluster")
    task_id = params.get("task_id")

    logger.info("skill_restart_start", service=service, cluster=cluster, task_id=task_id)
    start_time = time.time()

    try:
        from src.utils.aws_helpers import get_boto3_client
        ecs = get_boto3_client("ecs")

        if task_id:
            # Parar un task específico
            ecs.stop_task(
                cluster=cluster,
                task=task_id,
                reason=f"Kiro auto-remediation: restarting {service}",
            )
            logger.info("skill_restart_task_stopped", task_id=task_id, service=service)
        else:
            # Forzar un nuevo deploy (desired count cycle: 0 → original)
            svc_response = ecs.describe_services(cluster=cluster, services=[service])
            svcs = svc_response.get("services", [])
            if not svcs:
                raise ValueError(f"Service '{service}' not found in cluster '{cluster}'")
            original_count = svcs[0]["desiredCount"]

            ecs.update_service(cluster=cluster, service=service, forceNewDeployment=True)
            logger.info(
                "skill_restart_forced_deploy",
                service=service,
                cluster=cluster,
                desired_count=original_count,
            )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "skill": "restart_service",
            "status": "success",
            "service": service,
            "cluster": cluster,
            "task_id": task_id,
            "message": f"Service '{service}' restart initiated successfully",
            "duration_ms": elapsed_ms,
        }

    except Exception as exc:
        logger.error("skill_restart_failed", service=service, error=str(exc))
        return {
            "skill": "restart_service",
            "status": "failed",
            "service": service,
            "error": str(exc),
            "error_type": type(exc).__name__,
            "duration_ms": round((time.time() - start_time) * 1000, 2),
        }
