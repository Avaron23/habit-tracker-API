import concurrent.futures
import threading
from datetime import UTC, datetime
from unittest.mock import patch

import pytest
from fastapi import status
from fastapi.testclient import TestClient

url = "/habitlogs"


def test_habitlogs_create_habitlog_success(
    client: TestClient, auth_headers, habit_create_response
):
    habit_id = habit_create_response.json()["id"]

    response = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["habit_id"] == habit_id


def test_habitlogs_re_marking_in_the_same_period_returns_400(
    client: TestClient, auth_headers, habit_create_response
):
    habit_id = habit_create_response.json()["id"]
    client.post(url + f"/{habit_id}", headers=auth_headers)
    response = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Habit already logged for this daily period"


def test_habitlogs_getting_marks_history_success(
    client: TestClient, auth_headers, habit_create_response
):
    habit_id = habit_create_response.json()["id"]

    post_response = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert post_response.status_code == status.HTTP_201_CREATED

    response = client.get(url + f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["habit_id"] == habit_id


def test_habitlogs_marker_for_non_exist_habit_returns(
    client: TestClient, auth_headers, habit_create_response
):
    habit_id = 9999
    response = client.post(url + f"/{habit_id}", headers=auth_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Habit not found"


def test_habitlogs_marker_for_forbidden_habit_returns_error(
    client: TestClient,
    auth_headers,
    second_user,
    habit_create_response,
):
    second_user_habit_id = second_user["habit_id"]

    response = client.post(url + f"/{second_user_habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Habit not found"


def test_habitlogs_history_for_forbidden_habit_returns_error(
    client: TestClient,
    auth_headers,
    second_user,
    habit_create_response,
):
    second_user_habit_id = second_user["habit_id"]

    post_response = client.post(
        url + f"/{second_user_habit_id}", headers=second_user["headers"]
    )
    assert post_response.status_code == status.HTTP_201_CREATED

    response = client.get(url + f"/{second_user_habit_id}", headers=auth_headers)
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
    first_res = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert first_res.status_code == status.HTTP_201_CREATED

    mock_now.return_value = datetime(2026, 10, 12, 12, 30, tzinfo=UTC)
    response = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert datetime.fromisoformat(response.json()["date"]) == datetime(
        2026, 10, 12, 12, 30, tzinfo=UTC
    )


@patch("app.services.habitlog_service.get_now_utc")
def test_habitlogs_pagination_working(
    mock_now,
    client: TestClient,
    auth_headers,
    habit_create_response,
):
    habit_id = habit_create_response.json()["id"]

    mock_now.return_value = datetime(2026, 10, 11, 12, 30, tzinfo=UTC)
    first_res = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert first_res.status_code == status.HTTP_201_CREATED

    mock_now.return_value = datetime(2026, 10, 12, 12, 30, tzinfo=UTC)
    sec_response = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert sec_response.status_code == status.HTTP_201_CREATED

    mock_now.return_value = datetime(2026, 10, 13, 12, 30, tzinfo=UTC)
    first_res = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert first_res.status_code == status.HTTP_201_CREATED

    response = client.get(
        url + f"/{habit_id}", params={"limit": 1, "offset": 0}, headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) < 2

    second_response = client.get(
        url + f"/{habit_id}", params={"limit": 1, "offset": 1}, headers=auth_headers
    )
    assert second_response.status_code == status.HTTP_200_OK
    assert len(second_response.json()) < 2
    assert second_response.json()[0]["id"] == 2


@patch("app.services.habitlog_service.get_now_utc")
def test_habitlogs_weekly_marking_working(
    mock_now,
    client: TestClient,
    auth_headers,
):
    habit_create_response = client.post(
        "/habits",
        json={
            "title": "some-habit",
            "description": "some-description",
            "period": "weekly",
        },
        headers=auth_headers,
    )

    habit_id = habit_create_response.json()["id"]

    mock_now.return_value = datetime(2026, 10, 13, 12, 30, tzinfo=UTC)
    first_res = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert first_res.status_code == status.HTTP_201_CREATED

    mock_now.return_value = datetime(2026, 10, 19, 12, 30, tzinfo=UTC)
    response = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED


@patch("app.services.habitlog_service.get_now_utc")
def test_habitlogs_monthly_marking_working(
    mock_now,
    client: TestClient,
    auth_headers,
    habit_create_response,
):
    habit_create_response = client.post(
        "/habits",
        json={
            "title": "some-habit",
            "description": "some-description",
            "period": "monthly",
        },
        headers=auth_headers,
    )

    habit_id = habit_create_response.json()["id"]

    mock_now.return_value = datetime(2026, 10, 13, 12, 30, tzinfo=UTC)
    first_res = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert first_res.status_code == status.HTTP_201_CREATED

    mock_now.return_value = datetime(2026, 11, 2, 12, 30, tzinfo=UTC)
    response = client.post(url + f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED


def test_habitlogs_concurrent_create_only_one_succeeds(
    client: TestClient, auth_headers, habit_create_response
):
    habit_id = habit_create_response.json()["id"]

    # Небольшой "стартовый пистолет", чтобы оба потока рванули одновременно
    barrier = threading.Barrier(2)

    def make_request():
        barrier.wait()  # ждём, пока оба потока дойдут до этой точки
        return client.post(url + f"/{habit_id}", headers=auth_headers)

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(make_request) for _ in range(2)]
        responses = [f.result() for f in futures]

    statuses = sorted(r.status_code for r in responses)

    # Ровно один запрос должен победить, второй — получить 400
    assert statuses == [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]

    # Проверим, что в БД действительно одна метка
    get_response = client.get(url + f"/{habit_id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_200_OK
    assert len(get_response.json()) == 1


@pytest.mark.parametrize("limit, offset", [(0, 0), (101, 0), (1, -5)])
def test_habitlogs_invalid_pagination_params_returns_error(
    client: TestClient, auth_headers, habit_create_response, limit: int, offset: int
):
    habit_id = habit_create_response.json()["id"]

    response = client.get(
        url + f"/{habit_id}",
        params={"limit": limit, "offset": offset},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
