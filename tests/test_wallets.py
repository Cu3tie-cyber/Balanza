from fastapi.testclient import TestClient

from app.api.routes.wallets import wallets
from app.main import app

client = TestClient(app)


def setup_function():
    wallets.clear()


def test_create_wallet_returns_201():
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "Bolu's primary wallet",
            "currency": "NGN",
        },
    )

    assert response.status_code == 201

    body = response.json()
    assert body["name"] == "Bolu's primary wallet"
    assert body["currency"] == "NGN"
    assert body["balance_kobo"] == 0
    assert "id" in body


def test_get_existing_wallet_returns_200():
    create_response = client.post(
        "/api/v1/wallets",
        json={
            "name": "Savings wallet",
            "currency": "NGN",
        },
    )

    wallet_id = create_response.json()["id"]

    response = client.get(f"/api/v1/wallets/{wallet_id}")

    assert response.status_code == 200
    assert response.json()["id"] == wallet_id
    assert response.json()["name"] == "Savings wallet"


def test_get_missing_wallet_returns_404():
    response = client.get(
        "/api/v1/wallets/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Wallet not found"}


def test_invalid_wallet_input_returns_422():
    response = client.post(
        "/api/v1/wallets",
        json={
            "name": "A",
            "currency": "USD",
        },
    )

    assert response.status_code == 422