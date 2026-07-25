import asyncio
import uuid
import random
from src.models.logs import StructuredLogEvent, RequestDetail, ResponseDetail
from src.user_faker import generate_fake_user
from src.cloudwatch_client import cloudwatch_client

class TrafficGenerator:
    """
    Synthetic Production Traffic Simulation Engine.
    Executes background async loops simulating continuous customer transactions
    across all 8 domain microservices.
    """
    def __init__(self):
        self.is_running = False
        self.requests_per_second = 5
        self.error_rate_percentage = 10
        self.total_generated = 0
        self.total_errors = 0
        self._task: asyncio.Task = None

    def start(self, rps: int = 5, error_rate: int = 10):
        self.requests_per_second = rps
        self.error_rate_percentage = error_rate
        if not self.is_running:
            self.is_running = True
            self._task = asyncio.create_task(self._run_loop())

    def stop(self):
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()

    async def _run_loop(self):
        try:
            while self.is_running:
                delay = 1.0 / max(self.requests_per_second, 1)
                await asyncio.sleep(delay)
                self.generate_single_journey_step()
        except asyncio.CancelledError:
            pass

    def generate_single_journey_step(self):
        user = generate_fake_user()
        trace_id = f"tr-{uuid.uuid4().hex[:12]}"
        services = [
            ("login-service", "POST /api/v1/auth/login", {"dni": user.dni}),
            ("biometric-service", "POST /api/v1/biometric/verify", {"dni": user.dni, "full_name": user.full_name}),
            ("product-service", "GET /api/v1/products", {"category": "electronics"}),
            ("inventory-service", "GET /api/v1/inventory/stock/prod-101", {"product_id": "prod-101"}),
            ("address-validation-service", "POST /api/v1/address/validate", {"dni": user.dni, "address": "Av. Javier Prado 123"}),
            ("purchase-service", "POST /api/v1/purchase/checkout", {"dni": user.dni, "total": 199.90}),
            ("sales-service", "POST /api/v1/sales/pay", {"dni": user.dni, "amount": 199.90}),
            ("email-service", "POST /api/v1/notifications/email", {"email": user.email})
        ]
        
        svc, endpoint, body = random.choice(services)
        should_error = random.randint(1, 100) <= self.error_rate_percentage
        
        duration = random.uniform(15.0, 120.0) if not should_error else random.uniform(2000.0, 5000.0)
        status_code = 200 if not should_error else random.choice([500, 502, 503, 504])
        level = "INFO" if not should_error else "ERROR"
        
        error_type = None
        if should_error:
            error_type = random.choice([
                "DatabaseTimeoutError", "PaymentGatewayTimeoutError",
                "BiometricServiceFailure", "InventoryLockError"
            ])
            self.total_errors += 1

        event = StructuredLogEvent(
            level=level,
            service=svc,
            endpoint=endpoint,
            status_code=status_code,
            error_type=error_type,
            message="Request processed successfully" if not should_error else f"Failure during operation: {error_type}",
            trace_id=trace_id,
            duration_ms=round(duration, 2),
            user_context=user,
            request=RequestDetail(headers={"user-agent": "SimulatedUser/1.0"}, body=body),
            response=ResponseDetail(body={"status": "OK" if not should_error else "ERROR", "trace_id": trace_id})
        )
        cloudwatch_client.emit_log(event)
        self.total_generated += 1

    def generate_burst(self, count: int = 20):
        for _ in range(count):
            self.generate_single_journey_step()

traffic_generator = TrafficGenerator()
