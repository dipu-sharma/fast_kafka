import os
import asyncio
from aiokafka import AIOKafkaConsumer
import json

async def consume():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    consumer = AIOKafkaConsumer(
        'item_created',
        bootstrap_servers=bootstrap_servers,
        group_id='item_group'
    )
    await consumer.start()
    try:
        async for msg in consumer:
            print(f"Received: {json.loads(msg.value.decode('utf-8'))}")
    finally:
        await consumer.stop()

if __name__ == '__main__':
    asyncio.run(consume())