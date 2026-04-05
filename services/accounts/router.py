from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database import get_db
from . import service, schema
from typing import List

router = APIRouter(prefix="/accounts", tags=["Accounts"])

@router.post("/", response_model=schema.AccountRead)
async def create_account(account: schema.AccountCreate, db: AsyncSession = Depends(get_db)):
    return await service.create_account(db, account)

@router.get("/{account_id}", response_model=schema.AccountRead)
async def read_account(account_id: int, db: AsyncSession = Depends(get_db)):
    db_account = await service.get_account(db, account_id)
    if not db_account:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@router.get("/", response_model=List[schema.AccountRead])
async def list_accounts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await service.list_accounts(db, skip, limit)
