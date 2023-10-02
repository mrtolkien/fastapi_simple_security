"""Simple FastAPI security with a local SQLite database."""
from fastapi_sqlmodel_security.api_key_security import ApiKeySecurity
from fastapi_sqlmodel_security.data_store import DataStore, SqlModelDataStore
from fastapi_sqlmodel_security.endpoints import create_auth_router

__all__ = ["create_auth_router", "ApiKeySecurity", "DataStore", "SqlModelDataStore"]
