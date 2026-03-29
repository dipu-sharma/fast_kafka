import os
import asyncio
import json
import logging
from aiokafka import AIOKafkaConsumer

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("consumer")

async def consume():
    bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topics = ['transactions', 'accounts']
    
    consumer = AIOKafkaConsumer(
        *topics,
        bootstrap_servers=bootstrap_servers,
        group_id='banking_group',
        auto_offset_reset='earliest'
    )
    
    await consumer.start()
    logger.info(f"🚀 Banking consumer started on topics: {topics}")
    
    try:
        async for msg in consumer:
            try:
                payload = json.loads(msg.value.decode('utf-8'))
                topic = msg.topic
                logger.info(f"📩 Received from [{topic}]: {payload}")
                
                # Here you would add logic to handle different events
                # e.g., send an email on account creation or large withdrawal
                
            except Exception as e:
                logger.error(f"❌ Error decoding message: {e}")
                
    finally:
        await consumer.stop()
        logger.info("🛑 Consumer stopped")

if __name__ == '__main__':
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        pass
