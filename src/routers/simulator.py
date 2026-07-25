from fastapi import APIRouter
from src.traffic_generator import traffic_generator

router = APIRouter(prefix="/api/simulator", tags=["Traffic Simulator"])

@router.post("/start")
def start_simulator(rps: int = 5, error_rate: int = 10):
    traffic_generator.start(rps=rps, error_rate=error_rate)
    return {"status": "started", "rps": rps, "error_rate_percentage": error_rate}

@router.post("/stop")
def stop_simulator():
    traffic_generator.stop()
    return {"status": "stopped"}

@router.get("/status")
def simulator_status():
    return {
        "is_running": traffic_generator.is_running,
        "requests_per_second": traffic_generator.requests_per_second,
        "error_rate_percentage": traffic_generator.error_rate_percentage,
        "total_generated": traffic_generator.total_generated,
        "total_errors": traffic_generator.total_errors
    }

@router.post("/generate-burst")
def generate_burst(count: int = 20):
    traffic_generator.generate_burst(count=count)
    return {"status": "burst_generated", "count": count}
