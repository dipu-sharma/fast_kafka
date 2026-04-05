import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from common.database import engine
from common.kafka import start_producer, stop_producer
from services.accounts.router import router as accounts_router
from services.transactions.router import router as transactions_router
from services.profiles.router import router as profiles_router
from services.payments.router import router as payments_router

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

# reduce noisy Kafka logs
logging.getLogger('aiokafka').setLevel(logging.WARNING)
logging.getLogger('kafka').setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
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
app.include_router(profiles_router)
app.include_router(payments_router)
