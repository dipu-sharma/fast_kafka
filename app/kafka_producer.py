import os
from aiokafka import AIOKafkaProducer
import json
import asyncio

producer = None

async def get_producer():
    global producer
    if producer is None:
        bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        producer = AIOKafkaProducer(bootstrap_servers=bootstrap_servers)
        await producer.start()
    return producer

async def send_message(topic: str, message: dict):
    p = await get_producer()
    value = json.dumps(message).encode('utf-8')
    await p.send_and_wait(topic, value)