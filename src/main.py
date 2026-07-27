"""
E-Commerce Log Generator Microservice Entrypoint.
Provides synthetic production traffic generation, 8 domain microservice endpoints,
chaos fault injection, and CloudWatch / Local telemetry inspection.
"""

import asyncio
import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.cloudwatch_client import cloudwatch_client
from src.routers import health, e_commerce, chaos, simulator, logs, services, alerts

from src.traffic_generator import traffic_generator

logger = structlog.get_logger()
_flush_task: asyncio.Task = None
_auto_burst_task: asyncio.Task = None

app = FastAPI(
    title="E-Commerce Log Generator Microservice",
    description="Microservice for streaming production-like JSON logs to AWS CloudWatch & Local Inspector",
    version="1.0.0"
)

# Parse allowed CORS origins from settings
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(e_commerce.router)
app.include_router(chaos.router)
app.include_router(simulator.router)
app.include_router(logs.router)
app.include_router(services.router)
app.include_router(alerts.router)


def _ensure_log_group_exists():
    """Creates the CloudWatch Log Group if it doesn't exist."""
    try:
        from src.utils.aws_helpers import get_boto3_client
        client = get_boto3_client('logs')
        client.create_log_group(logGroupName=settings.LOG_GROUP_NAME)
        logger.info("log_group_created", log_group=settings.LOG_GROUP_NAME)
    except client.exceptions.ResourceAlreadyExistsException:
        pass
    except Exception as e:
        logger.warning("log_group_creation_failed", error=str(e))


async def _flush_loop():
    """Background loop that flushes buffered logs to CloudWatch every 5 seconds."""
    while True:
        await asyncio.sleep(5)
        try:
            count = cloudwatch_client.flush_to_cloudwatch()
            if count > 0:
                logger.info("cloudwatch_flush", events_flushed=count)
        except Exception as e:
            logger.error("cloudwatch_flush_error", error=str(e))


async def _auto_burst_loop():
    """Background loop that automatically generates exactly 10 logs every 3 minutes."""
    # Espera 10 segundos tras iniciar el microservicio para permitir que todo cargue correctamente
    await asyncio.sleep(10)
    while True:
        try:
            traffic_generator.generate_burst(count=10)
            logger.info("auto_burst_generated", count=10)
        except Exception as e:
            logger.error("auto_burst_failed", error=str(e))
        # Intervalo de 3 minutos (180 segundos)
        await asyncio.sleep(180)


@app.on_event("startup")
async def startup():
    global _flush_task, _auto_burst_task
    _ensure_log_group_exists()
    _flush_task = asyncio.create_task(_flush_loop())
    logger.info("flush_loop_started", interval_seconds=5, log_group=settings.LOG_GROUP_NAME)
    
    # Iniciar la generación automática de 10 logs cada 3 minutos
    _auto_burst_task = asyncio.create_task(_auto_burst_loop())
    logger.info("auto_burst_loop_started", interval_seconds=180, count=10)


@app.on_event("shutdown")
async def shutdown():
    global _flush_task, _auto_burst_task
    if _flush_task:
        _flush_task.cancel()
    if _auto_burst_task:
        _auto_burst_task.cancel()
    cloudwatch_client.flush_to_cloudwatch()
    logger.info("flush_loop_stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
