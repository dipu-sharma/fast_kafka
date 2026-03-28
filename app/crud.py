from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from . import models, schemas


# 🔹 GET SINGLE ITEM
async def get_item(db: AsyncSession, item_id: int):
    result = await db.execute(
        select(models.Item).where(models.Item.id == item_id)
    )
    return result.scalar_one_or_none()


# 🔹 GET MULTIPLE ITEMS (with pagination)
async def get_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    limit = min(limit, 100)  # safety cap

    result = await db.execute(
        select(models.Item)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


# 🔹 CREATE ITEM
async def create_item(db: AsyncSession, item: schemas.ItemCreate):
    db_item = models.Item(
        title=item.title,
        description=item.description
    )

    async with db.begin():  # ✅ transaction-safe
        db.add(db_item)

    await db.refresh(db_item)
    return db_item


# 🔥 UPDATE ITEM (NO SELECT → single query)
async def update_item(db: AsyncSession, item_id: int, item: schemas.ItemCreate):
    stmt = (
        update(models.Item)
        .where(models.Item.id == item_id)
        .values(
            title=item.title,
            description=item.description
        )
        .returning(models.Item)
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one_or_none()


# 🔥 DELETE ITEM (NO SELECT → single query)
async def delete_item(db: AsyncSession, item_id: int):
    stmt = (
        delete(models.Item)
        .where(models.Item.id == item_id)
        .returning(models.Item)
    )

    result = await db.execute(stmt)
    await db.commit()

    return result.scalar_one_or_none()


# 🚀 BULK CREATE (for 10 items/request use case)
async def create_items_bulk(db: AsyncSession, items: list[schemas.ItemCreate]):
    db_items = [
        models.Item(
            title=item.title,
            description=item.description
        )
        for item in items
    ]

    async with db.begin():
        db.add_all(db_items)

    return db_items