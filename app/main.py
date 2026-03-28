import logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from . import crud, models, schemas
from .database import AsyncSessionLocal, engine
from .kafka_producer import send_message, stop_producer, start_producer

# ✅ Proper logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# reduce noisy Kafka logs
logging.getLogger('aiokafka').setLevel(logging.WARNING)
logging.getLogger('kafka').setLevel(logging.WARNING)
logging.getLogger('kafka.conn').setLevel(logging.WARNING)


# ✅ Lifespan (correct)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB init
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    # Kafka start
    await start_producer()
    logger.info("✅ Kafka producer started")

    yield

    # Kafka stop
    await stop_producer()
    logger.info("🛑 Kafka producer stopped")


app = FastAPI(lifespan=lifespan)


# ✅ DB dependency (add rollback safety)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


# 🔥 CREATE ITEM (optimized)
@app.post("/items/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = await crud.create_item(db=db, item=item)

    # 🔥 NON-BLOCKING Kafka (important for performance)
    try:
        await send_message(
            "item_created",
            {
                "id": db_item.id,
                "title": db_item.title,
                "description": db_item.description
            }
        )
    except Exception as e:
        logger.warning(f"Kafka send failed (ignored): {e}")

    return db_item


# 🔹 READ LIST
@app.get("/items/", response_model=list[schemas.Item])
async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    limit = min(limit, 100)  # ✅ prevent abuse
    return await crud.get_items(db, skip=skip, limit=limit)


# 🔹 READ SINGLE
@app.get("/items/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db, item_id=item_id)

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return db_item


# 🔹 UPDATE
@app.put("/items/{item_id}", response_model=schemas.Item)
async def update_item(item_id: int, item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = await crud.update_item(db, item_id=item_id, item=item)

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return db_item


# 🔹 DELETE
@app.delete("/items/{item_id}", response_model=schemas.Item)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_item = await crud.delete_item(db, item_id=item_id)

    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return db_item


# ✅ Health check (VERY IMPORTANT for Docker/K8s)
@app.get("/health")
async def health():
    return {"status": "ok"}