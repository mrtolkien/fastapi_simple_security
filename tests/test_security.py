"""Basic unit testing.
"""
from fastapi.testclient import TestClient


def test_no_api_key(client: TestClient):
    response = client.get("/unsecured")
    assert response.status_code == 200

    response = client.get("/secure")
    assert response.status_code == 403


def get_api_key(client: TestClient, admin_key: str):
    response = client.get(url="/auth/new", headers={"secret-key": admin_key})
    assert response.status_code == 200

    return response.json()


def test_get_api_key(client: TestClient, admin_key: str):
    get_api_key(client, admin_key)


def test_query(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    response = client.get(url=f"/secure?api-key={api_key}")
    assert response.status_code == 200


def test_header(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    response = client.get("/secure", headers={"api-key": api_key})
    assert response.status_code == 200
