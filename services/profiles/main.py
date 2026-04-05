import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from services.profiles.router import router

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("profiles_service")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Profiles doesn't use Kafka producer currently, but for consistency:
    yield

app = FastAPI(
    title="Profiles Service",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "profiles"}

app.include_router(router)
