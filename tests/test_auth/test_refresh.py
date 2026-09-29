from datetime import UTC, datetime, timedelta
from http.cookies import SimpleCookie

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken

url = "/auth/refresh"


def test_refresh_returns_valid_access_token(client: TestClient, refresh_cookie):
    client.cookies.set("refresh_token", refresh_cookie)

    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK

    access_token = response.json()["access_token"]
    assert isinstance(access_token, str)
    assert access_token != ""


def test_refresh_rotates_cookie(client: TestClient, refresh_cookie):
    client.cookies.set("refresh_token", refresh_cookie)

    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] != ""
    assert response.cookies["refresh_token"] != refresh_cookie

    cookie = SimpleCookie()
    cookie.load(response.headers.get("set-cookie", ""))
    assert cookie["refresh_token"]["httponly"] is True


def test_refresh_new_cookie_works_after_rotation(client: TestClient, refresh_cookie):
    client.cookies.set("refresh_token", refresh_cookie)

    first = client.post(url)
    new_cookie = first.cookies["refresh_token"]

    client.cookies.set("refresh_token", new_cookie)
    second = client.post(url)

    assert second.status_code == status.HTTP_200_OK


def test_refresh_without_cookie_returns_401(
    client: TestClient,
):
    response = client.post(url=url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_random_token_returns_401(client: TestClient, refresh_cookie):
    random_token = "random-refresh-token"

    client.cookies["refresh_token"] = random_token

    response = client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_old_token_is_invalid(client: TestClient, refresh_cookie):
    old_token = refresh_cookie
    client.post(url)

    client.cookies["refresh_token"] = old_token

    response = client.post(url)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_refresh_expire_token_returns_401(
    client: TestClient, db_session: AsyncSession
):
    user_data = {
        "username": "test-user",
        "password": "strong-password",
        "timezone": "Europe/Moscow",
    }
    reg_res = client.post("/auth/register", json=user_data)

    reg_res_data = reg_res.json()
    user_id = reg_res_data["id"]

    client.post(
        "/auth/login", data={"username": "test-user", "password": "strong-password"}
    )

    refresh_db = await db_session.scalar(
        select(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .order_by(RefreshToken.expires_at.desc())
        .limit(1)
    )

    refresh_db.expires_at = datetime.now(UTC) - timedelta(minutes=5)

    await db_session.commit()

    ref_response = client.post(url)
    assert ref_response.status_code == status.HTTP_401_UNAUTHORIZED