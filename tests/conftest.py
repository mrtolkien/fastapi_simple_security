"""Pytest configuration.
"""
import time
import os

import pytest
from fastapi.testclient import TestClient

from app.main import app, db_location
from fastapi_sqlmodel_security.data_store import SqlModelDataStore

# The environment variable needs to be set before importing app
admin_key_value = "secret"
os.environ["FASTAPI_SQLMODEL_SECURITY_SECRET"] = admin_key_value

@pytest.fixture
def admin_key():
    return admin_key_value


@pytest.fixture
def client():
    os.remove(db_location) if os.path.exists(db_location) else None
    time.sleep(0.1)
    SqlModelDataStore(f"sqlite:///{db_location}")

    return TestClient(app)
