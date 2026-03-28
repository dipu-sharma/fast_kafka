import logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from . import crud, models, schemas
from .database import AsyncSessionLocal, engine
from .kafka_producer import send_message

# reduce noisy Kafka client logger output
logging.getLogger('aiokafka').setLevel(logging.WARNING)
logging.getLogger('kafka').setLevel(logging.WARNING)
logging.getLogger('kafka.conn').setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/items/", response_model=schemas.Item)
async def create_item(item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = await crud.create_item(db=db, item=item)
    try:
        await send_message("item_created", {"id": db_item.id, "title": db_item.title, "description": db_item.description})
    except Exception as e:
        print(f"Kafka send failed: {e}")
    return db_item

@app.get("/items/", response_model=list[schemas.Item])
async def read_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    items = await crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/{item_id}", response_model=schemas.Item)
async def read_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_item = await crud.get_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.put("/items/{item_id}", response_model=schemas.Item)
async def update_item(item_id: int, item: schemas.ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = await crud.update_item(db, item_id=item_id, item=item)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@app.delete("/items/{item_id}", response_model=schemas.Item)
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    db_item = await crud.delete_item(db, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item