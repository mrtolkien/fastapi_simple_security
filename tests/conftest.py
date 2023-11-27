"""Pytest configuration."""
import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import create_engine

from app.main import app, db_location
from fastapi_sqlmodel_security.data_store import SqlModelDataStore

# The environment variable needs to be set before importing app
admin_key_value = "secret"
os.environ["FASTAPI_SQLMODEL_SECURITY_SECRET"] = admin_key_value


@pytest.fixture(scope="module")
def admin_key():
    return admin_key_value


@pytest.fixture(scope="session")
def client():
    engine = create_engine(f"sqlite:///{db_location}")
    SqlModelDataStore(engine=engine)
    yield TestClient(app)
    engine.dispose()
    os.unlink(db_location) if os.path.exists(db_location) else None
