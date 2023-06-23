"""Basic unit testing.
"""
import os

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


def test_revoke(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    response = client.get("/secure", headers={"api-key": api_key})
    assert response.status_code == 200

    response = client.get(
        f"/auth/revoke?api-key={api_key}",
        headers={"secret-key": admin_key},
    )
    assert response.status_code == 200

    response = client.get("/secure", headers={"api-key": api_key})
    assert response.status_code == 403


def test_renew_basic(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    response = client.get(
        f"/auth/renew?api-key={api_key}",
        headers={"secret-key": admin_key},
    )

    assert response.status_code == 200


def test_renew_custom_date(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    response = client.get(
        f"/auth/renew?api-key={api_key}&expiration-date=2222-01-01",
        headers={"secret-key": admin_key},
    )

    assert response.status_code == 200


def test_renew_wrong_date(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    response = client.get(
        f"/auth/renew?api-key={api_key}&expiration-date=2222-22-22",
        headers={"secret-key": admin_key},
    )

    assert response.status_code == 422


def test_renew_wrong_key(client: TestClient, admin_key: str):
    response = client.get(
        "/auth/renew?api-key=123456",
        headers={"secret-key": admin_key},
    )

    assert response.status_code == 404


def test_renew_revoked(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    response = client.get(
        f"/auth/revoke?api-key={api_key}",
        headers={"secret-key": admin_key},
    )

    response = client.get(
        f"/auth/renew?api-key={api_key}",
        headers={"secret-key": admin_key},
    )

    assert response.status_code == 200
    assert "This API key was revoked and has been reactivated." in response.json()


def test_get_usage_stats(client: TestClient, admin_key: str):
    api_key = get_api_key(client, admin_key)

    for _ in range(5):
        client.get(url=f"/secure?api-key={api_key}")

    response = client.get("/auth/logs", headers={"secret-key": admin_key})

    assert response.status_code == 200

    assert response.json()["logs"][0]["total_queries"] == 5


def test_no_admin_key(client: TestClient):
    response = client.get(url="/auth/new")
    assert response.status_code == 403


def test_wrong_admin_key(client: TestClient):
    response = client.get(url="/auth/new", headers={"secret-key": "WRONG_SECRET_KEY"})
    assert response.status_code == 403


def test_no_secret():
    del os.environ["FASTAPI_SIMPLE_SECURITY_SECRET"]

    from fastapi_simple_security._security_secret import secret

    value = secret.get_secret_value()

    assert value != "secret"
    assert len(value) == 36
