"""
Skill: clear_cache
===================
Limpia el caché en memoria del Backend (in-memory deque de logs y servicios).
En una arquitectura con Redis, enviaría un FLUSHDB o DEL por patrón.

Risk level: MEDIUM — impacto controlado, no requiere confirmación.
IAM necesario: ninguno (operación local).
"""

import time
import structlog

logger = structlog.get_logger()


async def execute(params: dict) -> dict:
    """
    Limpia el caché en memoria del Backend.

    Params:
        target (str): Qué limpiar: 'logs' | 'services' | 'all' (default: 'logs')
        pattern (str, optional): Patrón de servicio (ej: 'sales-service')

    Returns:
        dict con items_cleared, status
    """
    target = params.get("target", "logs")
    pattern = params.get("pattern")

    logger.info("skill_clear_cache_start", target=target, pattern=pattern)
    start_time = time.time()

    try:
        cleared = 0

        if target in ("logs", "all"):
            from src.cloudwatch_client import cloudwatch_client
            before = len(cloudwatch_client._recent_events)
            cloudwatch_client._recent_events.clear()
            cloudwatch_client._logs_buffer.clear()
            cleared += before
            logger.info("skill_clear_cache_logs", cleared=before)

        if target in ("services", "all"):
            # Resetea el caché de logs de CloudWatch en el router
            import src.routers.logs as logs_router
            logs_router._cached_logs = []
            logs_router._cached_time = 0.0
            cleared += 1
            logger.info("skill_clear_cache_cloudwatch_cache")

        return {
            "skill": "clear_cache",
            "status": "success",
            "target": target,
            "pattern": pattern,
            "items_cleared": cleared,
            "message": f"Cache cleared successfully (target={target})",
            "duration_ms": round((time.time() - start_time) * 1000, 2),
        }

    except Exception as exc:
        logger.error("skill_clear_cache_failed", error=str(exc))
        return {
            "skill": "clear_cache",
            "status": "failed",
            "error": str(exc),
            "error_type": type(exc).__name__,
            "duration_ms": round((time.time() - start_time) * 1000, 2),
        }
