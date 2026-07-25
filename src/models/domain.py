from typing import List, Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    dni: str
    password: str

class LoginResponse(BaseModel):
    user_id: str
    token: str
    dni: str
    full_name: str

class BiometricVerifyRequest(BaseModel):
    dni: str
    full_name: str
    biometric_type: str = "FACIAL"

class BiometricVerifyResponse(BaseModel):
    dni: str
    verified: bool
    status: str

class InventoryReserveRequest(BaseModel):
    product_id: str
    quantity: int

class InventoryReserveResponse(BaseModel):
    reservation_id: str
    product_id: str
    quantity: int
    reserved: bool

class AddressValidateRequest(BaseModel):
    dni: str
    address: str
    city: str
    zip_code: str

class AddressValidateResponse(BaseModel):
    valid: bool
    ubigeo: str

class CheckoutRequest(BaseModel):
    dni: str
    cart_id: str
    items: List[dict]
    total_amount: float

class CheckoutResponse(BaseModel):
    order_id: str
    status: str
    total_amount: float

class PaymentRequest(BaseModel):
    order_id: str
    dni: str
    amount: float
    card_number_masked: str

class PaymentResponse(BaseModel):
    transaction_id: str
    status: str
    amount: float

class EmailNotificationRequest(BaseModel):
    email: str
    subject: str
    order_id: Optional[str] = None

class EmailNotificationResponse(BaseModel):
    notification_id: str
    delivered: bool
