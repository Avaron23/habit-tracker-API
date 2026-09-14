from fastapi import status, Depends
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pytest

from app.core.security import verify_password
from app.models.user import User


def test_register_user_successfully(
    client: TestClient,
    clean_database,
):
    user_data = {
        "username": "test-user",
        "password": "strong-password",
        "timezone": "Europe/Moscow"
    }

    response = client.post("/auth/register", json=user_data)

    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert response_data["username"] == user_data["username"]
    assert response_data["timezone"] == user_data["timezone"]
    assert isinstance(response_data["id"], int)
    assert response_data["id"] > 0
    assert "created_at" in response_data
    assert "password" not in response_data


def test_register_rejects_invalid_username(client: TestClient):
    user_data = {
        "username": "invalid user !",
        "password": "strong-password",
        "timezone": "Europe/Moscow"
    }

    response = client.post("/auth/register", json=user_data)

    response_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response_data


def test_register_rejects_invalid_timezone(client: TestClient):
    user_data = {
        "username": "test-user",
        "password": "strong-password",
        "timezone": "Invalid timezone"
    }

    response = client.post("/auth/register", json=user_data)

    response_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response_data


def test_register_rejects_request_data_without_required_param(client: TestClient):
    user_data = {
        "password": "strong-password",
        "timezone": "Invalid timezone"
    }

    response = client.post("/auth/register", json=user_data)

    response_data = response.json()

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
    assert "detail" in response_data


def test_register_rejects_existing_username(
    client: TestClient, 
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password",
        "timezone": "Europe/Moscow"
    }

    client.post("/auth/register", json=user_data)
    response = client.post("/auth/register", json=user_data)

    response_data = response.json()

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "detail" in response_data


def test_register_doesnt_return_password(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password",
        "timezone": "Europe/Moscow"
    }

    response = client.post("/auth/register", json=user_data)

    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert "password" not in response_data


@pytest.mark.anyio
async def test_register_in_bd_stored_hash_not_password(
    client: TestClient,
    db_session: AsyncSession
):
    user_data = {
        "username": "test-user",
        "password": "strong-password",
        "timezone": "Europe/Moscow"
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == status.HTTP_201_CREATED

    db_user = await db_session.scalar(
        select(User)
        .where(User.username == user_data["username"])
    )

    assert db_user is not None
    assert user_data["password"] != db_user.password_hash
    assert verify_password(
        user_data["password"], 
        db_user.password_hash
    )