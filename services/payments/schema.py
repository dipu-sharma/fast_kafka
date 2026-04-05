from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentMethodBase(BaseModel):
    type: str = Field(..., description="CREDIT_CARD or UPI")
    provider: str = Field(..., description="e.g. Stripe, Razorpay, Mock")
    identifier: str = Field(..., description="last4 or upi_id")

class PaymentMethodCreate(PaymentMethodBase):
    account_id: int

class PaymentMethodRead(PaymentMethodBase):
    id: int
    account_id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class CardPaymentRequest(BaseModel):
    account_id: int
    payment_method_id: int
    amount: float
    cvv: str = Field(..., min_length=3, max_length=4)

class UPIPaymentRequest(BaseModel):
    account_id: int
    payment_method_id: int
    amount: float
    upi_pin: str = Field(..., min_length=4, max_length=6)
