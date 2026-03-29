import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import engine, Base
from app.core.kafka_producer import start_producer, stop_producer
from app.accounts.router import router as accounts_router
from app.transactions.router import router as transactions_router

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# reduce noisy Kafka logs
logging.getLogger('aiokafka').setLevel(logging.WARNING)
logging.getLogger('kafka').setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # DB init
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ Database tables created/verified")

    # Kafka start
    await start_producer()
    logger.info("✅ Kafka producer started")

    yield

    # Kafka stop
    await stop_producer()
    logger.info("🛑 Kafka producer stopped")


app = FastAPI(
    title="Modular Banking API",
    description="A FastAPI banking application with Kafka integration and modular structure",
    version="1.0.0",
    lifespan=lifespan
)

# Health check
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

# Register Routers
app.include_router(accounts_router)
app.include_router(transactions_router)
