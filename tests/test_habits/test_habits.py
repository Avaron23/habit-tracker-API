from fastapi import status
from fastapi.testclient import TestClient
import pytest


url = "/habits"


def test_habits_create_habit_is_success(
    client: TestClient,
    auth_headers
):
    habit_data = {
        "title": "some-title",
        "description": "some-description",
        "period": "daily"
    }

    response = client.post(url, json=habit_data, headers=auth_headers)
    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    assert response_data["title"] == habit_data["title"]
    assert response_data["description"] == habit_data["description"]
    assert response_data["period"] == habit_data["period"]


def test_habits_current_user_no_habits_returns_empty_list(
    client: TestClient,
    auth_headers,
    second_user
):
    response = client.get(url, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data == []


def test_habits_created_habit_appears_in_list(
    client: TestClient,
    auth_headers
):
    habit_data = {
        "title": "some-title",
        "description": "some-description",
        "period": "daily"
    }

    post_response = client.post(url, json=habit_data, headers=auth_headers)
    assert post_response.status_code == status.HTTP_201_CREATED
    habit_id = post_response.json()["id"]

    response = client.get(url, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data != []
    assert response_data[0]["id"] == habit_id


def test_habits_get_habit_by_id(
    client: TestClient,
    auth_headers
):
    habit_data = {
        "title": "some-title",
        "description": "some-description",
        "period": "daily"
    }

    post_response = client.post(url, json=habit_data, headers=auth_headers)
    assert post_response.status_code == status.HTTP_201_CREATED
    habit_id = post_response.json()["id"]

    response = client.get(url+f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == habit_id


def test_habits_complete_habit_renewal(
    client: TestClient,
    auth_headers
):
    habit_data = {
        "title": "some-title",
        "description": "some-description",
        "period": "daily"
    }

    post_response = client.post(url, json=habit_data, headers=auth_headers)
    assert post_response.status_code == status.HTTP_201_CREATED
    habit_id = post_response.json()["id"]

    edited_habit_data = {
        "title": "some-title-edited",
        "description": "some-description-edited",
        "period": "weekly"  
    }
    response = client.put(url+f"/{habit_id}", json=edited_habit_data, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()
    assert response_data["id"] == habit_id
    assert response_data["title"] == edited_habit_data["title"]
    assert response_data["description"] == edited_habit_data["description"]
    assert response_data["period"] == edited_habit_data["period"]


def test_habits_delete_habit(
    client: TestClient,
    auth_headers
):
    habit_data = {
        "title": "some-title",
        "description": "some-description",
        "period": "daily"
    }

    post_response = client.post(url, json=habit_data, headers=auth_headers)
    assert post_response.status_code == status.HTTP_201_CREATED
    habit_id = post_response.json()["id"]

    response = client.delete(url+f"/{habit_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK

    get_res = client.get(url+f"/{habit_id}", headers=auth_headers)
    assert get_res.status_code == status.HTTP_404_NOT_FOUND


def test_habits_non_exist_id_returns_404(
    client: TestClient,
    auth_headers
):
    response = client.get(url+"/95", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND



@pytest.mark.parametrize(
    "field,value",
    [
        ("title", ""),
        ("title", "a" * 31),
        ("description", ""),
        ("period", "yearly"),
    ],
)
def test_habits_create_invalid_data_returns_422(
    client: TestClient,
    auth_headers,
    field: str,
    value,
):
    habit_data = {
        "title": "some-title",
        "description": "some-description",
        "period": "daily"
    }
    habit_data[field] = value

    response = client.post(
        url,
        json=habit_data,
        headers=auth_headers,
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT



def test_habits_user_cannot_see_other_users_habits(
    client: TestClient,
    auth_headers,
    second_user,
):
    response = client.get(url, headers=auth_headers)

    assert response.status_code == status.HTTP_200_OK

    habit_ids = [habit["id"] for habit in response.json()]
    assert second_user["habit_id"] not in habit_ids



@pytest.mark.parametrize(
    "method",
    ["GET", "PUT", "DELETE"],
)
def test_habits_user_cannot_access_other_users_habit(
    client: TestClient,
    auth_headers,
    second_user,
    method: str,
):
    habit_id = second_user["habit_id"]

    response = client.request(
        method,
        f"{url}/{habit_id}",
        headers=auth_headers,
        json={
            "title": "hacked-title",
            "description": "hacked-description",
            "period": "weekly",
        } if method == "PUT" else None,
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND