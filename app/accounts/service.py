from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core import models
from .schema import AccountCreate
from app.core.kafka_producer import send_message
from app.core.config import settings

async def create_account(db: AsyncSession, account: AccountCreate):
    db_account = models.Account(owner=account.owner)
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    
    # Notify Kafka 
    await send_message(settings.kafka_topic_accounts, {
        "event": "ACCOUNT_CREATED",
        "id": db_account.id,
        "owner": db_account.owner,
        "balance": db_account.balance
    })
    
    return db_account

async def get_account(db: AsyncSession, account_id: int):
    result = await db.execute(select(models.Account).where(models.Account.id == account_id))
    return result.scalar_one_or_none()

async def list_accounts(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Account).offset(skip).limit(limit))
    return result.scalars().all()
