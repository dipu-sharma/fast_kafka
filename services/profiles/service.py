from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from . import models
from .schema import ProfileUpdate

async def get_profile(db: AsyncSession, account_id: int):
    result = await db.execute(select(models.Profile).where(models.Profile.account_id == account_id))
    return result.scalar_one_or_none()

async def update_profile(db: AsyncSession, account_id: int, profile_update: ProfileUpdate):
    result = await db.execute(select(models.Profile).where(models.Profile.account_id == account_id))
    db_profile = result.scalar_one_or_none()
    
    if not db_profile:
        return None
    
    update_data = profile_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_profile, key, value)
    
    await db.commit()
    await db.refresh(db_profile)
    return db_profile
