# Microservice FastAPI Banking Application

A robust, asynchronous banking application built with FastAPI, PostgreSQL, and Kafka, refactored into a microservice-ready structure with Alembic migrations.

## Features
- **Microservice Architecture**: Independent services for Accounts, Payments, Profiles, and Transactions.
- **Database Migrations**: Centralized schema management using Alembic.
- **Event-Driven**: Services communicate asynchronously via Kafka events.
- **Shared Core**: Common logic (DB, Config, Kafka) resides in a shared `common/` package.
- **Atomic Transactions**: Secure money movement with PostgreSQL row-level locking.

## Project Structure
```
.
├── alembic/                # Database migrations
├── common/                 # Shared logic (DB, Config, Kafka)
├── services/               # Microservices
│   ├── accounts/           # Account management
│   ├── payments/           # 3rd party payment integration
│   ├── profiles/           # User profile management
│   └── transactions/       # Money movement (Deposit, Withdraw, Transfer)
├── consumer.py             # Global event consumer
├── main.py                 # Monolithic entry point (optional)
├── docker-compose.yml      # Orchestration for all services
└── Dockerfile
```

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the Application
Start all services (Postgres, Kafka, 4 Microservices, Consumer, and Migrations):
```bash
docker-compose up --build
```

### Service Endpoints
Each service runs on its own port:
- **Accounts Service**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Payments Service**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **Profiles Service**: [http://localhost:8003/docs](http://localhost:8003/docs)
- **Transactions Service**: [http://localhost:8004/docs](http://localhost:8004/docs)

## Database Migrations (Alembic)

Migrations are automatically applied when you run `docker-compose up`. 

### Generate a new migration
If you change any models in `services/*/models.py`, generate a new migration script:
```bash
docker-compose run --rm migrations alembic revision --autogenerate -m "describe your changes"
```

### Manually apply migrations
```bash
docker-compose run --rm migrations alembic upgrade head
```

## Technical Details
- **FastAPI**: High-performance web framework for each microservice.
- **SQLAlchemy 2.0 (Async)**: Asynchronous ORM with `asyncpg`.
- **Alembic**: Database migration tool.
- **AIOKafka**: Asynchronous Kafka integration.
- **Docker Multi-service**: Each module is containerized independently.
