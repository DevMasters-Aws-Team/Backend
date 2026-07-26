"""Services Router - Endpoint for frontend dashboard with dynamic service management."""

import time
import httpx
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

router = APIRouter(tags=["Services"])


class Microservice(BaseModel):
    """Microservice status model."""
    title: str
    name: str
    endpoint: str
    status: str = "ok"  # ok, warn, down
    reqs: str = "0"
    latency: str = "0 ms"
    bars: list[int] = Field(default_factory=lambda: [0] * 12)
    errorType: str = "none"  # none, warn, danger
    # Nuevos campos para servicios personalizados
    baseUrl: Optional[str] = None  # URL base del servicio (ej: http://localhost:8080)
    logGroup: Optional[str] = None  # CloudWatch Log Group name
    addedBy: str = "system"  # "system" para iniciales, "user" para agregados por usuario
    addedAt: Optional[str] = None


class AddServiceRequest(BaseModel):
    """Request model for adding a new microservice."""
    title: str = Field(..., min_length=1, max_length=100, description="Nombre descriptivo del servicio")
    name: str = Field(..., min_length=1, max_length=50, description="Nombre técnico del servicio")
    endpoint: str = Field(..., min_length=1, description="Endpoint del servicio (ej: /api/v1/users)")
    baseUrl: Optional[str] = Field(None, description="URL base opcional (ej: http://localhost:8080)")
    logGroup: Optional[str] = Field(None, description="CloudWatch Log Group name")


class ValidateEndpointRequest(BaseModel):
    """Request model for validating an endpoint."""
    endpoint: str = Field(..., description="Endpoint a validar")
    baseUrl: Optional[str] = Field(None, description="URL base opcional")


class ValidateEndpointResponse(BaseModel):
    """Response model for endpoint validation."""
    valid: bool
    reachable: bool
    statusCode: Optional[int] = None
    latencyMs: Optional[int] = None
    message: str
    suggestion: Optional[str] = None


# Initial microservices data matching frontend expectations
INITIAL_MICROSERVICES = [
    Microservice(
        title="Login & Autenticación",
        name="login-service",
        endpoint="/api/v1/auth/login",
        status="ok",
        reqs="12.4k",
        latency="45 ms",
        bars=[14, 18, 32, 24, 16, 8, 14, 8, 10, 8, 5, 2],
        errorType="none",
        addedBy="system",
    ),
    Microservice(
        title="Biometría & Verificación",
        name="biometric-service",
        endpoint="/api/v1/biometric/verify",
        status="warn",
        reqs="8.1k",
        latency="520 ms",
        bars=[10, 12, 18, 22, 28, 16, 20, 14, 12, 10, 8, 4],
        errorType="warn",
        addedBy="system",
    ),
    Microservice(
        title="Catálogo de Productos",
        name="product-service",
        endpoint="/api/v1/products",
        status="ok",
        reqs="15.2k",
        latency="65 ms",
        bars=[20, 24, 28, 34, 30, 22, 18, 16, 12, 10, 8, 5],
        errorType="none",
        addedBy="system",
    ),
    Microservice(
        title="Control de Inventario",
        name="inventory-service",
        endpoint="/api/v1/inventory/reserve",
        status="ok",
        reqs="6.8k",
        latency="80 ms",
        bars=[8, 12, 15, 18, 14, 10, 8, 12, 9, 6, 4, 2],
        errorType="none",
        addedBy="system",
    ),
    Microservice(
        title="Validación de Dirección",
        name="address-validation-service",
        endpoint="/api/v1/address/validate",
        status="ok",
        reqs="4.2k",
        latency="110 ms",
        bars=[6, 8, 10, 14, 12, 8, 6, 8, 5, 4, 3, 2],
        errorType="none",
        addedBy="system",
    ),
    Microservice(
        title="Procesador de Compras",
        name="purchase-service",
        endpoint="/api/v1/purchase/checkout",
        status="ok",
        reqs="5.5k",
        latency="135 ms",
        bars=[10, 12, 16, 20, 18, 12, 10, 8, 7, 5, 4, 2],
        errorType="none",
        addedBy="system",
    ),
    Microservice(
        title="Procesador de Ventas",
        name="sales-service",
        endpoint="/api/v1/sales/pay",
        status="down",
        reqs="3.1k",
        latency="3400 ms",
        bars=[12, 14, 22, 35, 30, 28, 24, 20, 18, 15, 12, 8],
        errorType="danger",
        addedBy="system",
    ),
    Microservice(
        title="Notificaciones por Email",
        name="email-service",
        endpoint="/api/v1/notifications/email",
        status="ok",
        reqs="2.9k",
        latency="90 ms",
        bars=[5, 6, 8, 10, 9, 7, 5, 4, 4, 3, 2, 1],
        errorType="none",
        addedBy="system",
    ),
]

# In-memory storage for services (in production, use database)
MICROSERVICES: list[Microservice] = list(INITIAL_MICROSERVICES)


@router.get("/api/services")
async def get_services() -> list[dict]:
    """Returns list of microservices for the frontend dashboard."""
    return [service.model_dump() for service in MICROSERVICES]


@router.post("/api/services")
async def add_service(request: AddServiceRequest) -> dict:
    """
    Add a new microservice to monitor.
    
    Flow:
    1. Validates endpoint availability (optional)
    2. Creates service entry
    3. Adds to monitoring list
    4. Returns the created service
    """
    # Check if service with same name already exists
    existing = next((s for s in MICROSERVICES if s.name == request.name), None)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Service with name '{request.name}' already exists"
        )
    
    # Create new service
    new_service = Microservice(
        title=request.title,
        name=request.name,
        endpoint=request.endpoint,
        status="ok",
        reqs="0",
        latency="0 ms",
        bars=[0] * 12,
        errorType="none",
        baseUrl=request.baseUrl,
        logGroup=request.logGroup,
        addedBy="user",
        addedAt=datetime.utcnow().isoformat(),
    )
    
    # Add to list
    MICROSERVICES.append(new_service)
    
    return {
        "status": "created",
        "service": new_service.model_dump(),
        "message": f"Service '{request.name}' added successfully",
        "next_steps": [
            "Configure CloudWatch Log Group for this service",
            "Ensure service sends structured JSON logs",
            "Set up EventBridge rule for error detection"
        ]
    }


@router.post("/api/services/validate")
async def validate_endpoint(request: ValidateEndpointRequest) -> ValidateEndpointResponse:
    """
    Validate if an endpoint is reachable and responding.
    
    This performs a health check on the endpoint.
    """
    # Build full URL
    base_url = request.baseUrl or "http://localhost:8000"
    full_url = f"{base_url.rstrip('/')}{request.endpoint}"
    
    try:
        start_time = time.time()
        
        # Make request with timeout
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(full_url)
            latency_ms = int((time.time() - start_time) * 1000)
            
            if response.status_code < 500:
                return ValidateEndpointResponse(
                    valid=True,
                    reachable=True,
                    statusCode=response.status_code,
                    latencyMs=latency_ms,
                    message=f"Endpoint is reachable (HTTP {response.status_code})",
                    suggestion="Endpoint is healthy and ready for monitoring"
                )
            else:
                return ValidateEndpointResponse(
                    valid=False,
                    reachable=True,
                    statusCode=response.status_code,
                    latencyMs=latency_ms,
                    message=f"Endpoint returned server error (HTTP {response.status_code})",
                    suggestion="Check service health before adding to monitoring"
                )
                
    except httpx.TimeoutException:
        return ValidateEndpointResponse(
            valid=False,
            reachable=False,
            message="Endpoint timed out after 5 seconds",
            suggestion="Check if service is running and accessible"
        )
    except httpx.ConnectError:
        return ValidateEndpointResponse(
            valid=False,
            reachable=False,
            message="Could not connect to endpoint",
            suggestion="Verify the URL and ensure service is running"
        )
    except Exception as e:
        return ValidateEndpointResponse(
            valid=False,
            reachable=False,
            message=f"Validation error: {str(e)}",
            suggestion="Check endpoint configuration"
        )


@router.delete("/api/services/{service_name}")
async def delete_service(service_name: str) -> dict:
    """Remove a microservice from monitoring."""
    global MICROSERVICES
    
    # Find service
    service_index = next((i for i, s in enumerate(MICROSERVICES) if s.name == service_name), None)
    
    if service_index is None:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )
    
    # Don't allow deleting initial services
    if MICROSERVICES[service_index].addedBy == "system":
        raise HTTPException(
            status_code=400,
            detail="Cannot delete system services. Only user-added services can be removed."
        )
    
    # Remove service
    removed_service = MICROSERVICES.pop(service_index)
    
    return {
        "status": "deleted",
        "service": removed_service.model_dump(),
        "message": f"Service '{service_name}' removed successfully"
    }


@router.get("/api/services/{service_name}")
async def get_service(service_name: str) -> dict:
    """Get details of a specific microservice."""
    service = next((s for s in MICROSERVICES if s.name == service_name), None)
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )
    
    return service.model_dump()


@router.put("/api/services/{service_name}")
async def update_service(service_name: str, request: AddServiceRequest) -> dict:
    """Update an existing microservice."""
    service = next((s for s in MICROSERVICES if s.name == service_name), None)
    
    if not service:
        raise HTTPException(
            status_code=404,
            detail=f"Service '{service_name}' not found"
        )
    
    # Update fields
    service.title = request.title
    service.endpoint = request.endpoint
    service.baseUrl = request.baseUrl
    service.logGroup = request.logGroup
    
    return {
        "status": "updated",
        "service": service.model_dump(),
        "message": f"Service '{service_name}' updated successfully"
    }
