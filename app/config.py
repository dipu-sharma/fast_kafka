import os
from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


def _build_db_url() -> str:
    user = os.getenv("POSTGRES_USER", "user")
    pw = os.getenv("POSTGRES_PASSWORD", "password")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "db")
    return f"postgresql+asyncpg://{user}:{pw}@{host}:{port}/{db}"


class Settings(BaseSettings):
    app_name: str = "FastAPI Kafka PostgreSQL"
    database_url: str = os.getenv("DATABASE_URL", _build_db_url())
    kafka_bootstrap_servers: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    kafka_topic: str = os.getenv("KAFKA_TOPIC", "item_created")

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
