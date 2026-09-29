from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pytest

from app.models.refresh_token import RefreshToken


url = "/auth/logout"


def test_logout_success(
    client: TestClient,
    login_response,
):
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Logout success"


def test_logout_success_delete_refresh_cookie(
    client: TestClient,
    login_response
):
    response = client.post(url)
    assert "refresh_token" not in response.cookies
    assert "refresh_token" not in client.cookies


@pytest.mark.anyio
async def test_logout_success_refresh_revoked(
    client: TestClient,
    db_session: AsyncSession
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

    client.post(url)

    refresh_token = await db_session.scalar(
        select(RefreshToken)
        .where(RefreshToken.user_id == user_id)
        .order_by(RefreshToken.expires_at.desc())
        .limit(1)
    )

    assert refresh_token.revoked


def test_logout_success_refresh_cookie_not_usable(
    client: TestClient,
    login_response
):
    refresh_token = client.cookies["refresh_token"]
    response = client.post(url)
    client.cookies["refresh_token"] = refresh_token

    refresh_response = client.post("/auth/refresh") 
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED