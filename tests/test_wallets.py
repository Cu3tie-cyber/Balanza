from fastapi.testclient import TestClient


def create_wallet(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "Test Wallet",
            "currency": "NGN",
        },
    )

    assert response.status_code == 201

    return response.json()


def create_transaction(
    client: TestClient,
    wallet_id: str,
    transaction_type: str,
    amount_kobo: int,
) -> dict:
    response = client.post(
        f"/api/v1/wallets/{wallet_id}/transactions",
        json={
            "transaction_type": transaction_type,
            "amount_kobo": amount_kobo,
        },
    )

    assert response.status_code == 201

    return response.json()


def test_create_wallet_starts_with_zero_balance(
    client: TestClient,
) -> None:
    wallet = create_wallet(client)

    assert wallet["name"] == "Test Wallet"
    assert wallet["currency"] == "NGN"
    assert wallet["balance_kobo"] == 0
    assert "id" in wallet
    assert "created_at" in wallet
    assert "updated_at" in wallet


def test_get_wallet(
    client: TestClient,
) -> None:
    created_wallet = create_wallet(client)

    response = client.get(
        f"/api/v1/wallets/{created_wallet['id']}"
    )

    assert response.status_code == 200

    wallet = response.json()

    assert wallet["id"] == created_wallet["id"]
    assert wallet["name"] == "Test Wallet"
    assert wallet["balance_kobo"] == 0


def test_credit_increases_wallet_balance(
    client: TestClient,
) -> None:
    wallet = create_wallet(client)

    transaction = create_transaction(
        client=client,
        wallet_id=wallet["id"],
        transaction_type="credit",
        amount_kobo=50_000,
    )

    assert transaction["wallet_id"] == wallet["id"]
    assert transaction["transaction_type"] == "credit"
    assert transaction["amount_kobo"] == 50_000

    wallet_response = client.get(
        f"/api/v1/wallets/{wallet['id']}"
    )

    assert wallet_response.status_code == 200
    assert wallet_response.json()["balance_kobo"] == 50_000


def test_debit_decreases_wallet_balance(
    client: TestClient,
) -> None:
    wallet = create_wallet(client)

    create_transaction(
        client=client,
        wallet_id=wallet["id"],
        transaction_type="credit",
        amount_kobo=50_000,
    )

    transaction = create_transaction(
        client=client,
        wallet_id=wallet["id"],
        transaction_type="debit",
        amount_kobo=20_000,
    )

    assert transaction["transaction_type"] == "debit"
    assert transaction["amount_kobo"] == 20_000

    wallet_response = client.get(
        f"/api/v1/wallets/{wallet['id']}"
    )

    assert wallet_response.status_code == 200
    assert wallet_response.json()["balance_kobo"] == 30_000


def test_insufficient_debit_does_not_change_balance(
    client: TestClient,
) -> None:
    wallet = create_wallet(client)

    create_transaction(
        client=client,
        wallet_id=wallet["id"],
        transaction_type="credit",
        amount_kobo=10_000,
    )

    response = client.post(
        f"/api/v1/wallets/{wallet['id']}/transactions",
        json={
            "transaction_type": "debit",
            "amount_kobo": 15_000,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient wallet balance"

    wallet_response = client.get(
        f"/api/v1/wallets/{wallet['id']}"
    )

    assert wallet_response.status_code == 200
    assert wallet_response.json()["balance_kobo"] == 10_000


def test_list_transactions_returns_wallet_ledger(
    client: TestClient,
) -> None:
    wallet = create_wallet(client)

    create_transaction(
        client=client,
        wallet_id=wallet["id"],
        transaction_type="credit",
        amount_kobo=50_000,
    )

    create_transaction(
        client=client,
        wallet_id=wallet["id"],
        transaction_type="debit",
        amount_kobo=20_000,
    )

    response = client.get(
        f"/api/v1/wallets/{wallet['id']}/transactions"
    )

    assert response.status_code == 200

    transactions = response.json()

    assert len(transactions) == 2
    assert {item["transaction_type"] for item in transactions} == {
        "credit",
        "debit",
    }
    assert {item["amount_kobo"] for item in transactions} == {
        50_000,
        20_000,
    }
    assert all(
        item["wallet_id"] == wallet["id"]
        for item in transactions
    )


def test_invalid_transaction_amount_is_rejected(
    client: TestClient,
) -> None:
    wallet = create_wallet(client)

    response = client.post(
        f"/api/v1/wallets/{wallet['id']}/transactions",
        json={
            "transaction_type": "credit",
            "amount_kobo": 0,
        },
    )

    assert response.status_code == 422


def test_invalid_transaction_type_is_rejected(
    client: TestClient,
) -> None:
    wallet = create_wallet(client)

    response = client.post(
        f"/api/v1/wallets/{wallet['id']}/transactions",
        json={
            "transaction_type": "transfer",
            "amount_kobo": 5_000,
        },
    )

    assert response.status_code == 422