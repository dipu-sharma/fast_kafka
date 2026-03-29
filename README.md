# Modular FastAPI Banking Application

A robust, asynchronous banking application built with FastAPI, PostgreSQL, and Kafka.

## Features
- **Account Management**: Create and view accounts with real-time balance tracking.
- **Transactions**: Secure deposits, withdrawals, and transfers with atomic database transactions.
- **Event-Driven**: All major actions (account creation, transactions) emit events to Kafka.
- **Modular Architecture**: Clean separation of concerns with module-wise organization (`router`, `service`, `schema`).
- **Resilient Kafka Producer**: Built-in retry logic and automatic topic provisioning.

## Project Structure
```
.
├── main.py                 # Application entry point
├── app/
│   ├── core/               # Shared core logic (DB, Config, Kafka, Models)
│   ├── accounts/           # Account management module
│   │   ├── router.py
│   │   ├── service.py
│   │   └── schema.py
│   └── transactions/       # Money movement module
│       ├── router.py
│       ├── service.py
│       └── schema.py
├── consumer.py             # Standalone background event consumer
├── docker-compose.yml
└── Dockerfile
```

## Getting Started

### Prerequisites
- Docker and Docker Compose

### Running the Application
1. **Start all services**:
   ```bash
   docker-compose up --build
   ```
2. **Access the API Documentation**:
   Open [http://localhost:8000/docs](http://localhost:8000/docs) in your browser.

3. **Run the Background Consumer**:
   (In a separate terminal, ensure you have dependencies installed)
   ```bash
   python consumer.py
   ```

## API Endpoints

### Accounts
- `POST /accounts/`: Create a new bank account.
- `GET /accounts/`: List all accounts.
- `GET /accounts/{id}`: Get account details and balance.

### Transactions
- `POST /transactions/deposit`: Add funds to an account.
- `POST /transactions/withdraw`: Remove funds from an account (checks for sufficient balance).
- `POST /transactions/transfer`: Transfer money between two accounts (atomic operation).
- `GET /transactions/history/{account_id}`: View transaction history for an account.

## Technical Details
- **FastAPI**: Modern, fast (high-performance) web framework.
- **SQLAlchemy 2.0 (Async)**: Asynchronous ORM with `asyncpg`.
- **AIOKafka**: Asynchronous Kafka client for Python.
- **Pydantic v2**: Data validation and settings management.
