from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from common.database import get_db
from . import service, schema

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.get("/{account_id}", response_model=schema.ProfileRead)
async def read_profile(account_id: int, db: AsyncSession = Depends(get_db)):
    db_profile = await service.get_profile(db, account_id)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile

@router.patch("/{account_id}", response_model=schema.ProfileRead)
async def update_profile(account_id: int, profile: schema.ProfileUpdate, db: AsyncSession = Depends(get_db)):
    db_profile = await service.update_profile(db, account_id, profile)
    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return db_profile
