from fastapi.testclient import TestClient


def test_root_returns_success_response(client: TestClient):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Hello world!!!"
    } 


def test_unknown_route_returns_not_found(client: TestClient):
    response = client.get("/unknown")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Not Found",
    }