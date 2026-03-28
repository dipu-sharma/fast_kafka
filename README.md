# FastAPI Kafka PostgreSQL CRUD

This is a FastAPI application with Kafka and PostgreSQL for CRUD operations on Items.

## Setup

1. Start the services: `docker-compose up -d`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `uvicorn app.main:app --reload`

## API

- POST /items/ - Create item
- GET /items/ - List items
- GET /items/{id} - Get item
- PUT /items/{id} - Update item
- DELETE /items/{id} - Delete item

## Kafka Consumer

Run `python consumer.py` to see messages when items are created.