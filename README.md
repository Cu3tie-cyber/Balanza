# Balanza 

A reliability-focused fintech backend API built with Python, FastAPI, and PostgreSQL. It explores safe internal wallet transfers under retries, concurrent requests, and authorization checks.

> Status: Actively under development.

## Why this project exists

Financial APIs must remain correct even when clients retry requests, networks fail, two requests happen at once, or a user tries to access data they do not own.

Balanza is an in-progress project designed to explore those backend engineering problems. It does not process real payments, store card data, or hold real customer funds.

## Current capabilities

- FastAPI application
- `GET /health` health-check endpoint
- Automatically generated interactive API documentation at `/docs`
- Versioned API routing under `/api/v1`
- `POST /api/v1/wallets` creates a persistent NGN wallet in PostgreSQL
- `GET /api/v1/wallets/{wallet_id}` retrieves a persistent wallet by UUID
- Alembic database migrations manage the PostgreSQL schema
- Automated endpoint tests run against an isolated PostgreSQL test database
- Pydantic request validation for wallet name and supported currency
- Consistent `404 Not Found` responses for missing wallets

## Planned capabilities

- Project configuration and environment-variable management
- PostgreSQL database integration and schema migrations
- User registration and login
- Protected API routes
- Wallet creation and balance lookup
- Input validation and consistent API errors
- Transaction-safe wallet transfers
- Append-only ledger entries
- Idempotency keys for money-moving requests
- Ownership and authorization tests
- Concurrent-transfer tests
- Simulated payment-provider webhooks
- Audit logs and structured application logs

## Tech stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Docker Compose
- Pytest

## Project structure

```text
ledgerlite-api/
├── app/
│   ├── main.py
│   ├── auth/
│   ├── wallets/
│   ├── transfers/
│   └── common/
├── tests/
├── docs/
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Getting started

### Prerequisites

- Python 3.12 or later
- Docker and Docker Compose
- Git

### Run locally

```bash
git clone [https://github.com/YOUR-GITHUB-USERNAME/ledgerlite-api.git](https://github.com/YOUR-GITHUB-USERNAME/ledgerlite-api.git)
cd ledgerlite-api

cp .env.example .env

docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Interactive API documentation will be available at:

```text
http://localhost:8000/docs
```

## API examples

### Check service health

```http
GET /health
```

Example response:

```json
{
  "status": "ok"
}
```

### Register a user

```http
POST /auth/register
Content-Type: application/json
```

```json
{
  "email": "bolu@example.com",
  "password": "a-strong-password"
}
```

## Testing

Run the test suite with:

```bash
pytest
```

The project will include tests for successful behaviour as well as failure cases such as invalid input, unauthorized access, duplicate requests, and insufficient balance.
The current test suite verifies wallet creation, successful retrieval, missing-wallet handling, and request validation against an isolated PostgreSQL test database.

## Architecture decisions

### Why FastAPI?

FastAPI was chosen because Python is my strongest language and it supports explicit request validation, type hints, generated API documentation, and fast iteration.

### Why PostgreSQL?

PostgreSQL was chosen because this project requires relational data modelling, database constraints, and transactions for operations that must remain consistent.

### Why a modular monolith?

This project is intentionally a modular monolith rather than microservices. A single application and database make transaction boundaries easier to reason about while the code remains organized by domain.

### Why integer kobo for money?

Currency amounts will be stored as integer kobo values. For example, ₦5,000.00 is represented as `500000` kobo. This avoids floating-point precision errors.

## Known limitations

- This is not a licensed financial service.
- It does not process real payments or store payment-card information.
- Payment-provider interactions are simulated.
- It is not production-ready without further security review, monitoring, load testing, deployment hardening, and compliance work.

## Testing

Activate the virtual environment and run:

```powershell
pytest
```

The current test suite verifies wallet creation, successful retrieval, missing-wallet handling, and request validation.

## Local PostgreSQL

Balanza uses PostgreSQL for local development through Docker Compose.

1. Copy the environment template:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Start PostgreSQL:

   ```powershell
   docker compose up -d db
   ```

3. Confirm the database is healthy:

   ```powershell
   docker compose ps
   ```

4. Stop the database without deleting its stored data:

   ```powershell
   docker compose down
   ```

The PostgreSQL data is stored in a local Docker volume and survives normal container restarts.

- GitHub: https://github.com/YOUR-GITHUB-USERNAME
- Location: Abuja, Nigeria
