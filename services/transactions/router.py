from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database import get_db
from . import service, schema
from typing import List

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/deposit", response_model=schema.TransactionRead)
async def deposit(transaction: schema.TransactionCreate, db: AsyncSession = Depends(get_db)):
    return await service.deposit(db, transaction)

@router.post("/withdraw", response_model=schema.TransactionRead)
async def withdraw(transaction: schema.TransactionCreate, db: AsyncSession = Depends(get_db)):
    return await service.withdraw(db, transaction)

@router.post("/transfer", response_model=schema.TransactionRead)
async def transfer(transfer: schema.TransferCreate, db: AsyncSession = Depends(get_db)):
    return await service.transfer(db, transfer)

@router.get("/history/{account_id}", response_model=List[schema.TransactionRead])
async def read_history(account_id: int, db: AsyncSession = Depends(get_db)):
    return await service.get_history(db, account_id)
