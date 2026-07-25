"""
E-Commerce Log Generator Microservice Entrypoint.
Provides synthetic production traffic generation, 8 domain microservice endpoints,
chaos fault injection, and CloudWatch / Local telemetry inspection.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.routers import health, e_commerce, chaos, simulator, logs

app = FastAPI(
    title="E-Commerce Log Generator Microservice",
    description="Microservice for streaming production-like JSON logs to AWS CloudWatch & Local Inspector",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(e_commerce.router)
app.include_router(chaos.router)
app.include_router(simulator.router)
app.include_router(logs.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
