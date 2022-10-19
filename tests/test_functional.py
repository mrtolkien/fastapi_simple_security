"""Basic unit testing.
"""
import sqlite3

from fastapi.testclient import TestClient

from fastapi_simple_security._sqlite_access import sqlite_access

# TODO Rename test files and group them properly (db tests, endpoints tests, ...)


def test_database_migration():
    # Emulate old db
    with sqlite3.connect(sqlite_access.db_location) as connection:
        c = connection.cursor()
        # Create database
        c.execute(
            """
    CREATE TABLE IF NOT EXISTS fastapi_simple_security (
        api_key TEXT PRIMARY KEY,
        is_active INTEGER,
        never_expire INTEGER,
        expiration_date TEXT,
        latest_query_date TEXT,
        total_queries INTEGER)
    """
        )
        connection.commit()

    # Apply migration
    sqlite_access.init_db()

    # Test of the migration execution
    with sqlite3.connect(sqlite_access.db_location) as connection:
        c = connection.cursor()
        c.execute("PRAGMA table_info(fastapi_simple_security);")
        columns = c.fetchall()
        assert len(columns) == 7, columns  # Colum 'name' created


def test_api_key_name(client: TestClient, admin_key: str):
    response = client.get(
        url="/auth/new", headers={"secret-key": admin_key}, params={"name": "Test"}
    )
    assert response.status_code == 200

    response = client.get("/auth/logs", headers={"secret-key": admin_key})
    assert response.status_code == 200
    assert len(response.json()["logs"]) == 1
    api_key_infos = response.json()["logs"][0]
    assert api_key_infos.get("name") == "Test", api_key_infos


def test_api_key_never_expire(client: TestClient, admin_key: str):
    # Create with never_expires param
    response = client.get(
        url="/auth/new",
        headers={"secret-key": admin_key},
        params={"never_expires": True},
    )
    assert response.status_code == 200

    response = client.get("/auth/logs", headers={"secret-key": admin_key})
    assert response.status_code == 200
    assert len(response.json()["logs"]) == 1
    api_key_infos = response.json()["logs"][0]
    assert api_key_infos.get("never_expire") is True, api_key_infos
