"""Pytest configuration.
"""
import os

import pytest
from fastapi.testclient import TestClient

# The environment variable needs to be set before importing app
admin_key_value = "secret"
os.environ["FASTAPI_SIMPLE_SECURITY_SECRET"] = admin_key_value

from app.main import app  # pylint: disable=wrong-import-position


@pytest.fixture
def admin_key():
    return admin_key_value


@pytest.fixture
def client():
    return TestClient(app)
