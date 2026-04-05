import random
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from . import models
from .schema import PaymentMethodCreate, CardPaymentRequest, UPIPaymentRequest
from services.transactions import service as tx_service
from services.transactions.schema import TransactionCreate
from common.kafka import send_message
from common.config import settings

async def register_payment_method(db: AsyncSession, pm_in: PaymentMethodCreate):
    db_pm = models.PaymentMethod(**pm_in.model_dump())
    db.add(db_pm)
    await db.commit()
    await db.refresh(db_pm)
    return db_pm

async def list_payment_methods(db: AsyncSession, account_id: int):
    result = await db.execute(select(models.PaymentMethod).where(models.PaymentMethod.account_id == account_id, models.PaymentMethod.is_active == True))
    return result.scalars().all()

async def process_external_payment(db: AsyncSession, account_id: int, payment_method_id: int, amount: float, method_type: str):
    # Verify payment method
    result = await db.execute(select(models.PaymentMethod).where(models.PaymentMethod.id == payment_method_id, models.PaymentMethod.account_id == account_id))
    pm = result.scalar_one_or_none()
    
    if not pm or not pm.is_active:
        raise HTTPException(status_code=400, detail="Invalid or inactive payment method")
    
    if pm.type != method_type:
        raise HTTPException(status_code=400, detail=f"Payment method is not of type {method_type}")

    # Simulate 3rd party processing delay
    await asyncio.sleep(0.5)
    
    # Simulate success/failure (90% success)
    if random.random() > 0.9:
        raise HTTPException(status_code=402, detail="Payment declined by external provider")

    # If successful, perform deposit
    tx_in = TransactionCreate(account_id=account_id, amount=amount)
    db_tx = await tx_service.deposit(db, tx_in)
    
    # Update transaction with payment method
    db_tx.payment_method_id = payment_method_id
    await db.commit()
    await db.refresh(db_tx)
    
    # Send specific payment event to Kafka
    await send_message(settings.kafka_topic_transactions, {
        "event": "THIRD_PARTY_PAYMENT_SUCCESS",
        "account_id": account_id,
        "payment_method_id": payment_method_id,
        "amount": amount,
        "provider": pm.provider,
        "type": method_type
    })
    
    return db_tx
