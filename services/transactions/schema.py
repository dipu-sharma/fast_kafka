from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    amount: float

    @field_validator('amount')
    @classmethod
    def amount_must_be_positive(cls, v: float) -> float:
        if v <= 0:
            raise ValueError('amount must be positive')
        return v

class TransactionCreate(TransactionBase):
    account_id: int

class TransferCreate(TransactionBase):
    from_account_id: int
    to_account_id: int

class TransactionRead(TransactionBase):
    id: int
    account_id: int
    transaction_type: str
    related_account_id: Optional[int]
    payment_method_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
