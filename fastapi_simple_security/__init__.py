"""Simple FastAPI security with a local SQLite database.
"""
from fastapi_simple_security.endpoints import api_key_router
from fastapi_simple_security.security_api_key import api_key_security

__all__ = ["api_key_router", "api_key_security"]
