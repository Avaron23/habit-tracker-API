from http.cookies import SimpleCookie

from fastapi.testclient import TestClient
from fastapi import status

from app.core.config import settings


url = "/auth/login"


def test_login_successfully(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data)

    assert response.status_code == status.HTTP_200_OK


def test_login_returns_access_token(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data)
    response_data = response.json()

    assert "access_token" in response_data
    assert isinstance(response_data["access_token"], str)
    assert response_data["access_token"] != ""


def test_login_returns_bearer_token_type(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data)
    response_data = response.json()

    assert response_data["token_type"] == "bearer"


def test_login_returns_expected_expires_in(
    client: TestClient,
    clean_database
):
    expected = settings.access_token_expire_minutes * 60
    user_data = {
        "username": "test-user",
        "password": "strong-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data)
    response_data = response.json()

    assert response_data["expires_in"] == expected


def test_login_returns_refresh_token_cookie(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data)

    assert "refresh_token" in response.cookies
    assert response.cookies["refresh_token"] != ""


def test_login_refresh_token_is_httponly(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data)

    set_cookie = response.headers.get("set-cookie", "")
    cookie = SimpleCookie()
    cookie.load(set_cookie)

    assert "refresh_token" in cookie
    morsel = cookie["refresh_token"]

    assert morsel["httponly"] is True


def test_login_invalid_password_returns_401(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "invalid-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data) 
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response_data


def test_login_non_existent_user_returns_401(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "strong-password"
    }

    response = client.post(url, data=user_data) 
    response_data = response.json()

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response_data


def test_login_invalid_password_nonexistent_user_both_returns_401(
    client: TestClient,
    clean_database
):
    user_data = {
        "username": "test-user",
        "password": "invalid-password"
    }

    user_data_2 = {
        "username": "test-user-second",
        "password": "strong-password"
    }

    client.post("/auth/register", json={
        "username": "test-user",
        "password":"strong-password",
        "timezone": "Europe/Moscow"
    })

    response = client.post(url, data=user_data) 
    response_2 = client.post(url, data=user_data_2)

    assert response.status_code == response_2.status_code == status.HTTP_401_UNAUTHORIZED