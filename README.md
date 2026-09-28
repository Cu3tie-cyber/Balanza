# Balanza

Balanza is a reliability-focused fintech wallet backend built with Python, FastAPI, PostgreSQL, SQLAlchemy, and Alembic.

It implements a simple NGN wallet ledger with database constraints, transactional credit and debit operations, and automated API tests. Balanza is a learning project: it does not process real payments, store card data, or hold real customer funds.

> Status: MVP complete. Authentication, idempotency, and production deployment hardening are planned next.

## Features

- FastAPI application with interactive Swagger documentation.
- Versioned API routes under `/api/v1`.
- PostgreSQL persistence through SQLAlchemy.
- Alembic database migrations.
- Create NGN wallets with a zero starting balance.
- Retrieve wallet details by UUID.
- Credit and debit wallet balances using integer kobo values.
- Append-only transaction ledger entries.
- Debit protection: insufficient-balance debits return `400 Bad Request`.
- Database constraints:
  - Wallet balances cannot be negative.
  - Transaction amounts must be greater than zero.
  - Transaction types are restricted to `credit` and `debit`.
  - Every transaction must reference an existing wallet.
- Row locking during transaction processing to help prevent concurrent debits from overdrawing a wallet.
- Automated endpoint tests using an isolated PostgreSQL test database.

## Tech Stack

- Python 3.12
- FastAPI
- Pydantic v2
- PostgreSQL 16
- SQLAlchemy
- Alembic
- Psycopg
- Docker Compose
- Pytest
- HTTPX

## Project Structure

```text
Balanza/
|-- alembic/
|   |-- versions/
|   `-- env.py
|-- app/
|   |-- api/
|   |   |-- routes/
|   |   |   `-- wallets.py
|   |   `-- router.py
|   |-- core/
|   |   `-- config.py
|   |-- db/
|   |   |-- base.py
|   |   `-- session.py
|   |-- models/
|   |   |-- transaction.py
|   |   `-- wallet.py
|   |-- schemas/
|   |   |-- transaction.py
|   |   `-- wallet.py
|   `-- main.py
|-- tests/
|   |-- conftest.py
|   `-- test_wallets.py
|-- compose.yaml
|-- requirements.txt
|-- .env.example
`-- README.md
```

## Prerequisites

- Python 3.12 or later
- Docker Desktop with Docker Compose
- Git

## Local Setup

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 3. Create the environment file

```powershell
Copy-Item .env.example .env
```

Use the local-development values in `.env.example` unless you need to change your PostgreSQL user, password, or port.

### 4. Start PostgreSQL

```powershell
docker compose up -d db
```

Confirm that the database is healthy:

```powershell
docker compose ps
```

### 5. Apply database migrations

```powershell
alembic upgrade head
```

### 6. Start the API

```powershell
uvicorn app.main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Returns application health information |
| `POST` | `/api/v1/wallets` | Creates a wallet with a zero balance |
| `GET` | `/api/v1/wallets/{wallet_id}` | Retrieves one wallet |
| `POST` | `/api/v1/wallets/{wallet_id}/transactions` | Credits or debits a wallet |
| `GET` | `/api/v1/wallets/{wallet_id}/transactions` | Lists a wallet transaction ledger |

## API Examples

### Create a wallet

```http
POST /api/v1/wallets
Content-Type: application/json
```

```json
{
  "name": "Primary Wallet",
  "currency": "NGN"
}
```

A successful response returns `201 Created` and starts with:

```json
{
  "balance_kobo": 0
}
```

### Credit a wallet

```http
POST /api/v1/wallets/{wallet_id}/transactions
Content-Type: application/json
```

```json
{
  "transaction_type": "credit",
  "amount_kobo": 50000
}
```

`50000` kobo represents NGN 500.00.

### Debit a wallet

```http
POST /api/v1/wallets/{wallet_id}/transactions
Content-Type: application/json
```

```json
{
  "transaction_type": "debit",
  "amount_kobo": 20000
}
```

A debit larger than the available balance returns:

```text
400 Bad Request
```

```json
{
  "detail": "Insufficient wallet balance"
}
```

## Transaction Safety

Each credit or debit operation:

1. Locks the target wallet row while processing the request.
2. Checks available balance before a debit.
3. Updates the wallet balance.
4. Creates the matching transaction ledger entry.
5. Commits both changes together.

If a debit is larger than the available balance, Balanza returns an error and does not create a transaction or change the balance.

## Testing

The automated test suite runs against the separate `balanza_test` PostgreSQL database, not the normal development database.

Create and migrate the test database once:

```powershell
docker compose exec db psql -U balanza -d postgres -c "CREATE DATABASE balanza_test;"
```

If the database already exists, PostgreSQL will report that it exists; this is safe to ignore.

Apply migrations to the test database:

```powershell
$env:POSTGRES_DB = "balanza_test"
alembic upgrade head
Remove-Item Env:POSTGRES_DB
```

Run the tests:

```powershell
pytest -v
```

The current suite verifies:

- Wallet creation with a zero balance.
- Wallet retrieval.
- Successful credits.
- Successful debits.
- Insufficient-funds rejection without changing the balance.
- Transaction-ledger retrieval.
- Invalid amount rejection.
- Invalid transaction-type rejection.

## Known Limitations

- No user accounts or authentication yet.
- No wallet ownership or authorization checks yet.
- No idempotency keys for safe client retries yet.
- No external payment-provider integration.
- No audit log beyond the wallet transaction ledger.
- No production deployment configuration, monitoring, rate limiting, or compliance review.
- This application is not a licensed financial service and must not be used to handle real funds.