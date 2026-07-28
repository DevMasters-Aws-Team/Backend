"""
Skills Registry
================
Registro centralizado de todas las skills de remediación disponibles.
El Agente Carmen consulta este registry para saber qué acciones puede ejecutar.
"""

from typing import Callable

SKILLS_REGISTRY: dict[str, dict] = {
    "restart_service": {
        "description": "Reinicia un servicio/task ECS cuando hay fallos irrecuperables (HTTP 500 persistente, memory leak)",
        "risk_level": "high",
        "requires_confirmation": True,
        "iam_permissions": ["ecs:StopTask", "ecs:UpdateService", "ecs:DescribeTasks"],
        "params": {
            "service": "str — nombre del servicio",
            "cluster": "str — nombre del cluster ECS (default: kiro-cluster)",
            "task_id": "str (opcional) — ARN del task específico",
        },
    },
    "scale_up": {
        "description": "Escala horizontalmente un servicio ECS (CPU > 80%, latencia P99 alta, error rate > 5%)",
        "risk_level": "medium",
        "requires_confirmation": True,
        "iam_permissions": ["ecs:UpdateService", "ecs:DescribeServices"],
        "params": {
            "service": "str — nombre del servicio",
            "cluster": "str — nombre del cluster",
            "desired_count": "int — nuevo número de tasks",
            "max_count": "int (opcional) — límite máximo (default: 10)",
        },
    },
    "clear_cache": {
        "description": "Limpia el caché en memoria (respuestas inconsistentes, datos stale detectados)",
        "risk_level": "medium",
        "requires_confirmation": False,
        "iam_permissions": [],
        "params": {
            "target": "str — 'logs' | 'services' | 'all'",
            "pattern": "str (opcional) — patrón de servicio a limpiar",
        },
    },
    "rotate_connections": {
        "description": "Rota el connection pool de AWS cuando hay timeouts persistentes de conexión",
        "risk_level": "low",
        "requires_confirmation": False,
        "iam_permissions": [],
        "params": {
            "service": "str — nombre del servicio afectado",
            "pool_size": "int (opcional) — nuevo tamaño del pool",
        },
    },
    "send_alert": {
        "description": "Envía notificación al equipo via SNS/log cuando se requiere intervención humana",
        "risk_level": "low",
        "requires_confirmation": False,
        "iam_permissions": ["sns:Publish"],
        "params": {
            "severity": "str — critical | high | medium | low",
            "message": "str — descripción del incidente",
            "service": "str — servicio afectado",
            "context": "dict (opcional) — datos adicionales",
            "channel": "str (opcional) — 'sns' | 'log'",
        },
    },
}


async def invoke_skill(skill_name: str, params: dict) -> dict:
    """
    Invoca una skill por nombre. Entry point usado por el Agente Carmen.

    Args:
        skill_name: Nombre de la skill (debe estar en SKILLS_REGISTRY)
        params: Parámetros específicos de la skill

    Returns:
        dict con resultado de la ejecución

    Raises:
        ValueError: Si la skill no existe en el registry
    """
    if skill_name not in SKILLS_REGISTRY:
        available = list(SKILLS_REGISTRY.keys())
        raise ValueError(
            f"Skill '{skill_name}' not found. Available skills: {available}"
        )

    # Import dinámico del módulo de la skill
    import importlib
    module = importlib.import_module(f"src.skills.{skill_name}")
    result = await module.execute(params)
    return result
