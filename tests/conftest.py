from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.session import get_db
from app.main import app


test_engine = create_engine(
    settings.test_database_url,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_test_database() -> Generator[None, None, None]:
    with test_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE transactions, wallets "
                "RESTART IDENTITY CASCADE"
            )
        )

    yield

    with test_engine.begin() as connection:
        connection.execute(
            text(
                "TRUNCATE TABLE transactions, wallets "
                "RESTART IDENTITY CASCADE"
            )
        )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()