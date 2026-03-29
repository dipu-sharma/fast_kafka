from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException
from app.core import models
from .schema import TransactionCreate, TransferCreate
from app.core.kafka_producer import send_message
from app.core.config import settings

async def deposit(db: AsyncSession, transaction: TransactionCreate):
    async with db.begin():
        # Get account
        result = await db.execute(select(models.Account).where(models.Account.id == transaction.account_id).with_for_update())
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        # Update balance
        account.balance += transaction.amount
        
        # Create record
        db_transaction = models.Transaction(
            account_id=transaction.account_id,
            amount=transaction.amount,
            transaction_type="DEPOSIT"
        )
        db.add(db_transaction)
    
    await db.refresh(db_transaction)
    
    # Notify Kafka
    await send_message(settings.kafka_topic_transactions, {
        "event": "DEPOSIT",
        "account_id": transaction.account_id,
        "amount": transaction.amount,
        "new_balance": account.balance
    })
    
    return db_transaction

async def withdraw(db: AsyncSession, transaction: TransactionCreate):
    async with db.begin():
        # Get account
        result = await db.execute(select(models.Account).where(models.Account.id == transaction.account_id).with_for_update())
        account = result.scalar_one_or_none()
        if not account:
            raise HTTPException(status_code=404, detail="Account not found")

        if account.balance < transaction.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Update balance
        account.balance -= transaction.amount
        
        # Create record
        db_transaction = models.Transaction(
            account_id=transaction.account_id,
            amount=transaction.amount,
            transaction_type="WITHDRAWAL"
        )
        db.add(db_transaction)
    
    await db.refresh(db_transaction)

    # Notify Kafka
    await send_message(settings.kafka_topic_transactions, {
        "event": "WITHDRAWAL",
        "account_id": transaction.account_id,
        "amount": transaction.amount,
        "new_balance": account.balance
    })

    return db_transaction

async def transfer(db: AsyncSession, transfer: TransferCreate):
    async with db.begin():
        # Get from_account
        result_from = await db.execute(select(models.Account).where(models.Account.id == transfer.from_account_id).with_for_update())
        from_account = result_from.scalar_one_or_none()
        
        # Get to_account
        result_to = await db.execute(select(models.Account).where(models.Account.id == transfer.to_account_id).with_for_update())
        to_account = result_to.scalar_one_or_none()

        if not from_account or not to_account:
            raise HTTPException(status_code=404, detail="One or both accounts not found")

        if from_account.balance < transfer.amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Update balances
        from_account.balance -= transfer.amount
        to_account.balance += transfer.amount
        
        # Create transaction records
        tx_out = models.Transaction(
            account_id=transfer.from_account_id,
            amount=transfer.amount,
            transaction_type="TRANSFER_OUT",
            related_account_id=transfer.to_account_id
        )
        tx_in = models.Transaction(
            account_id=transfer.to_account_id,
            amount=transfer.amount,
            transaction_type="TRANSFER_IN",
            related_account_id=transfer.from_account_id
        )
        db.add_all([tx_out, tx_in])
    
    await db.refresh(tx_out)

    # Notify Kafka
    await send_message(settings.kafka_topic_transactions, {
        "event": "TRANSFER",
        "from_account_id": transfer.from_account_id,
        "to_account_id": transfer.to_account_id,
        "amount": transfer.amount
    })

    return tx_out

async def get_history(db: AsyncSession, account_id: int):
    result = await db.execute(select(models.Transaction).where(models.Transaction.account_id == account_id).order_by(models.Transaction.created_at.desc()))
    return result.scalars().all()
