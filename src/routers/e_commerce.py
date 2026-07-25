import uuid
import time
from fastapi import APIRouter
from src.models.domain import (
    LoginRequest, LoginResponse, BiometricVerifyRequest, BiometricVerifyResponse,
    InventoryReserveRequest, InventoryReserveResponse, AddressValidateRequest,
    AddressValidateResponse, CheckoutRequest, CheckoutResponse, PaymentRequest,
    PaymentResponse, EmailNotificationRequest, EmailNotificationResponse
)
from src.models.logs import StructuredLogEvent, RequestDetail, ResponseDetail, UserContext
from src.user_faker import generate_fake_user
from src.cloudwatch_client import cloudwatch_client

router = APIRouter(prefix="/api/v1", tags=["E-Commerce Microservices"])

# 1. Login Service
@router.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest):
    start = time.time()
    user = generate_fake_user()
    user.dni = req.dni
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    
    res = LoginResponse(
        user_id=f"usr-{req.dni}",
        token=f"jwt-{uuid.uuid4().hex}",
        dni=req.dni,
        full_name=user.full_name
    )
    
    event = StructuredLogEvent(
        level="INFO",
        service="login-service",
        endpoint="POST /api/v1/auth/login",
        status_code=200,
        message="User authentication successful",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(body={"dni": req.dni}),
        response=ResponseDetail(body=res.model_dump())
    )
    cloudwatch_client.emit_log(event)
    return res

# 2. Biometric Service
@router.post("/biometric/verify", response_model=BiometricVerifyResponse)
def verify_biometric(req: BiometricVerifyRequest):
    start = time.time()
    user = UserContext(dni=req.dni, full_name=req.full_name, email=f"{req.dni}@ficticio.com", ip_address="190.234.10.1")
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    
    res = BiometricVerifyResponse(dni=req.dni, verified=True, status="BIOMETRIC_MATCH")
    
    event = StructuredLogEvent(
        level="INFO",
        service="biometric-service",
        endpoint="POST /api/v1/biometric/verify",
        status_code=200,
        message="Biometric verification matched RENIEC database",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(body=req.model_dump()),
        response=ResponseDetail(body=res.model_dump())
    )
    cloudwatch_client.emit_log(event)
    return res

# 3. Product Service
@router.get("/products")
def list_products(category: str = "all"):
    start = time.time()
    user = generate_fake_user()
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    products = [
        {"product_id": "prod-101", "name": "Smartphone Galaxy S24", "category": "Mobile", "price": 3499.00, "in_stock": True},
        {"product_id": "prod-102", "name": "Laptop Lenovo ThinkPad", "category": "Computers", "price": 4200.00, "in_stock": True}
    ]
    event = StructuredLogEvent(
        level="INFO",
        service="product-service",
        endpoint="GET /api/v1/products",
        status_code=200,
        message="Product catalog queried",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(query_params={"category": category}),
        response=ResponseDetail(body={"count": len(products)})
    )
    cloudwatch_client.emit_log(event)
    return products

# 4. Inventory Service
@router.post("/inventory/reserve", response_model=InventoryReserveResponse)
def reserve_inventory(req: InventoryReserveRequest, dni: str = "77889900"):
    start = time.time()
    user = generate_fake_user()
    user.dni = dni
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    res = InventoryReserveResponse(reservation_id=f"res-{uuid.uuid4().hex[:8]}", product_id=req.product_id, quantity=req.quantity, reserved=True)
    
    event = StructuredLogEvent(
        level="INFO",
        service="inventory-service",
        endpoint="POST /api/v1/inventory/reserve",
        status_code=200,
        message="Inventory stock reserved",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(body=req.model_dump()),
        response=ResponseDetail(body=res.model_dump())
    )
    cloudwatch_client.emit_log(event)
    return res

# 5. Address Validation Service
@router.post("/address/validate", response_model=AddressValidateResponse)
def validate_address(req: AddressValidateRequest):
    start = time.time()
    user = generate_fake_user()
    user.dni = req.dni
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    res = AddressValidateResponse(valid=True, ubigeo="150101")
    
    event = StructuredLogEvent(
        level="INFO",
        service="address-validation-service",
        endpoint="POST /api/v1/address/validate",
        status_code=200,
        message="Shipping address coverage validated",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(body=req.model_dump()),
        response=ResponseDetail(body=res.model_dump())
    )
    cloudwatch_client.emit_log(event)
    return res

# 6. Purchase Service
@router.post("/purchase/checkout", response_model=CheckoutResponse)
def checkout(req: CheckoutRequest):
    start = time.time()
    user = generate_fake_user()
    user.dni = req.dni
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    
    res = CheckoutResponse(order_id=f"ord-{uuid.uuid4().hex[:8]}", status="CHECKOUT_COMPLETED", total_amount=req.total_amount)
    
    event = StructuredLogEvent(
        level="INFO",
        service="purchase-service",
        endpoint="POST /api/v1/purchase/checkout",
        status_code=200,
        message="Purchase checkout completed successfully",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(body=req.model_dump()),
        response=ResponseDetail(body=res.model_dump())
    )
    cloudwatch_client.emit_log(event)
    return res

# 7. Sales Service
@router.post("/sales/pay", response_model=PaymentResponse)
def process_payment(req: PaymentRequest):
    start = time.time()
    user = generate_fake_user()
    user.dni = req.dni
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    
    res = PaymentResponse(transaction_id=f"tx-{uuid.uuid4().hex[:8]}", status="APPROVED", amount=req.amount)
    
    event = StructuredLogEvent(
        level="INFO",
        service="sales-service",
        endpoint="POST /api/v1/sales/pay",
        status_code=200,
        message="Payment processed successfully",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(body=req.model_dump()),
        response=ResponseDetail(body=res.model_dump())
    )
    cloudwatch_client.emit_log(event)
    return res

# 8. Email Service
@router.post("/notifications/email", response_model=EmailNotificationResponse)
def send_email(req: EmailNotificationRequest, dni: str = "77889900"):
    start = time.time()
    user = generate_fake_user()
    user.dni = dni
    user.email = req.email
    trace_id = f"tr-{uuid.uuid4().hex[:12]}"
    res = EmailNotificationResponse(notification_id=f"notif-{uuid.uuid4().hex[:8]}", delivered=True)
    
    event = StructuredLogEvent(
        level="INFO",
        service="email-service",
        endpoint="POST /api/v1/notifications/email",
        status_code=200,
        message="Notification receipt email sent",
        trace_id=trace_id,
        duration_ms=round((time.time() - start) * 1000, 2),
        user_context=user,
        request=RequestDetail(body=req.model_dump()),
        response=ResponseDetail(body=res.model_dump())
    )
    cloudwatch_client.emit_log(event)
    return res
