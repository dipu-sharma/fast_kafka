import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from common.database import engine, Base
from common.kafka import start_producer, stop_producer
from services.accounts.router import router

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("accounts_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Kafka start
    await start_producer()
    logger.info("✅ Kafka producer started for Accounts Service")
    yield
    # Kafka stop
    await stop_producer()
    logger.info("🛑 Kafka producer stopped for Accounts Service")

app = FastAPI(
    title="Accounts Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "accounts"}

app.include_router(router)
