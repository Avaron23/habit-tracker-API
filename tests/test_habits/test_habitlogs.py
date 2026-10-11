from datetime import datetime, UTC, timedelta

from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import patch

url = "/habitlogs"


def test_habitlogs_create_habitlog_success(
    client: TestClient,
    auth_headers,
    habit_create_response
):
    habit_id = habit_create_response.json()["id"]

    response = client.post(url+f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["habit_id"] == habit_id


def test_habitlogs_re_marking_in_the_same_period_returns_400(
    client: TestClient,
    auth_headers,
    habit_create_response
):
    habit_id = habit_create_response.json()["id"]
    first_response = client.post(url+f"/{habit_id}", headers=auth_headers)
    response = client.post(url+f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Habit already logged for this daily period"


def test_habitlogs_getting_marks_history_success(
    client: TestClient,
    auth_headers,
    habit_create_response
):
    habit_id = habit_create_response.json()["id"]

    post_response = client.post(url+f"/{habit_id}", headers=auth_headers)
    assert post_response.status_code == status.HTTP_201_CREATED

    response = client.get(url+f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["habit_id"] == habit_id


def test_habitlogs_marker_for_non_exist_habit_returns(
    client: TestClient,
    auth_headers,
    habit_create_response
):
    habit_id = 9999
    response = client.post(url+f"/{habit_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Habit not found"


def test_habitlogs_marker_for_forbidden_habit_returns_error(
    client: TestClient,
    auth_headers,
    second_user,
    habit_create_response,
):
    second_user_habit_id = second_user["habit_id"]

    response = client.post(url+f"/{second_user_habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Habit not found"


def test_habitlogs_history_for_forbidden_habit_returns_error(
    client: TestClient,
    auth_headers,
    second_user,
    habit_create_response,
):
    second_user_habit_id = second_user["habit_id"]

    post_response = client.post(url+f"/{second_user_habit_id}", headers=second_user["headers"])
    assert post_response.status_code == status.HTTP_201_CREATED

    response = client.get(url+f"/{second_user_habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Habit not found"


@patch("app.services.habitlog_service.get_now_utc")
def test_habitlogs_new_mark_in_another_day_success(
    mock_now,
    client: TestClient,
    auth_headers,
    habit_create_response,
):
    habit_id = habit_create_response.json()["id"]

    mock_now.return_value = datetime(2026, 10, 11, 12, 30, tzinfo=UTC)
    first_res = client.post(url+f"/{habit_id}", headers=auth_headers)
    assert first_res.status_code == status.HTTP_201_CREATED

    mock_now.return_value = datetime(2026, 10, 12, 12, 30, tzinfo=UTC)
    response = client.post(url+f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert datetime.fromisoformat(response.json()["date"]) == datetime(2026, 10, 12, 12, 30, tzinfo=UTC)