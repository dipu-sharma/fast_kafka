from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database import get_db
from . import service, schema
from services.transactions.schema import TransactionRead
from typing import List

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/methods", response_model=schema.PaymentMethodRead)
async def register_payment_method(pm: schema.PaymentMethodCreate, db: AsyncSession = Depends(get_db)):
    return await service.register_payment_method(db, pm)

@router.get("/methods/{account_id}", response_model=List[schema.PaymentMethodRead])
async def list_payment_methods(account_id: int, db: AsyncSession = Depends(get_db)):
    return await service.list_payment_methods(db, account_id)

@router.post("/charge/card", response_model=TransactionRead)
async def charge_card(req: schema.CardPaymentRequest, db: AsyncSession = Depends(get_db)):
    # Simulating external card charge
    return await service.process_external_payment(
        db, req.account_id, req.payment_method_id, req.amount, "CREDIT_CARD"
    )

@router.post("/charge/upi", response_model=TransactionRead)
async def charge_upi(req: schema.UPIPaymentRequest, db: AsyncSession = Depends(get_db)):
    # Simulating external UPI charge
    return await service.process_external_payment(
        db, req.account_id, req.payment_method_id, req.amount, "UPI"
    )
