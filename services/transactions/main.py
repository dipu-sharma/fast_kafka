import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from common.kafka import start_producer, stop_producer
from services.transactions.router import router

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("transactions_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kafka start
    await start_producer()
    logger.info("✅ Kafka producer started for Transactions Service")
    yield
    # Kafka stop
    await stop_producer()
    logger.info("🛑 Kafka producer stopped for Transactions Service")

app = FastAPI(
    title="Transactions Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "transactions"}

app.include_router(router)
