import json
import asyncio
import logging
from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import (
    UnknownTopicOrPartitionError,
    BrokerNotAvailableError,
    KafkaError
)

from .config import settings

logger = logging.getLogger("app.kafka")

producer = None
producer_lock = asyncio.Lock()
topic_lock = asyncio.Lock()
topic_initialized = False


async def ensure_topics():
    global topic_initialized

    async with topic_lock:
        if topic_initialized:
            return

        admin = None
        try:
            admin = AIOKafkaAdminClient(
                bootstrap_servers=settings.kafka_bootstrap_servers
            )
            await admin.start()

            existing_topics = await admin.list_topics()
            required_topics = [settings.kafka_topic_transactions, settings.kafka_topic_accounts]

            new_topics = []
            for topic in required_topics:
                if topic not in existing_topics:
                    new_topics.append(NewTopic(
                        name=topic,
                        num_partitions=1,
                        replication_factor=1
                    ))

            if new_topics:
                await admin.create_topics(new_topics)
                logger.info(f"✅ Created topics: {[t.name for t in new_topics]}")

            topic_initialized = True

        except Exception as e:
            logger.warning(f"⚠️ Topic creation skipped or failed: {e}")

        finally:
            if admin:
                try:
                    await admin.stop()
                except Exception:
                    pass


async def get_producer():
    global producer

    if producer and not producer._closed:
        return producer

    async with producer_lock:
        if producer and not producer._closed:
            return producer

        retries = 7

        for attempt in range(1, retries + 1):
            try:
                producer = AIOKafkaProducer(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8")
                )

                await producer.start()

                logger.info("✅ Kafka producer connected")
                return producer

            except (BrokerNotAvailableError, KafkaError) as e:
                backoff = min(1.5 ** attempt, 10)
                logger.warning(
                    f"❌ Kafka connection failed (attempt {attempt}): {e}, retry in {backoff:.2f}s"
                )
                await asyncio.sleep(backoff)

        logger.error("❌ Kafka unavailable after retries")
        producer = None
        return None


async def send_message(topic: str, message: dict):
    p = await get_producer()

    if not p:
        logger.warning("⚠️ Kafka unavailable, skipping message")
        return

    try:
        await p.send(topic, message)
        logger.info(f"✅ Sent to Kafka → {topic}: {message}")

    except UnknownTopicOrPartitionError:
        logger.warning(f"⚠️ Topic {topic} missing, retrying after creation")
        await ensure_topics()
        await p.send(topic, message)

    except Exception as e:
        logger.warning(f"⚠️ Kafka send failed: {e}")


async def stop_producer():
    global producer

    if producer:
        await producer.stop()
        producer = None
        logger.info("🛑 Kafka producer stopped")


async def start_producer():
    await ensure_topics()
    await get_producer()
