from fastapi import status
from fastapi.testclient import TestClient


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