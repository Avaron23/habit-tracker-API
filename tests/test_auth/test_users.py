from fastapi import status
from fastapi.testclient import TestClient

from app.models.refresh_token import RefreshToken
from app.core.security import create_access_token


url = "/users/me"


def test_users_me_with_valid_access_returns_user(
    client: TestClient,
    registered_user,
    auth_headers
):
    response = client.get(url, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert data["username"] == registered_user["username"]
    assert data["id"] == registered_user["id"]
    assert data["timezone"] == registered_user["timezone"]
    assert "password" not in data
    assert "password_hash" not in data


def test_users_me_without_access_returns_401(
    client: TestClient,
    login_response
):
    response = client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_users_me_with_invalid_token_returns_401(
    client: TestClient,
    login_response
):
    access_token = "invalid_token"
    response = client.get(url, headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_users_me_with_nonexist_user_id_returns_401(
    client: TestClient,
    login_response
):
    access_token = create_access_token({"sub": "invalid_id"})
    response = client.get(url, headers={"Authorization": f"Bearer {access_token}"})

    assert response.status_code == status.HTTP_401_UNAUTHORIZED