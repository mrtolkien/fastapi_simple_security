"""Main dependency for other endpoints."""
from fastapi import Security
from fastapi.security import APIKeyHeader, APIKeyQuery
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

from fastapi_sqlmodel_security.data_store import DataStore

API_KEY_NAME = "x-api-key"

api_key_query = APIKeyQuery(
    name=API_KEY_NAME, scheme_name="API key query", auto_error=False
)
api_key_header = APIKeyHeader(
    name=API_KEY_NAME, scheme_name="API key header", auto_error=False
)


class ApiKeySecurity:

    def __init__(self, data_store: DataStore):
        self.data_store = data_store

    def __call__(self, 
        query_param: str = Security(api_key_query),
        header_param: str = Security(api_key_header),
    ):
        if not query_param and not header_param:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="An API key must be passed as query or header",
            )

        elif query_param and self.data_store.check_key(query_param):
            return query_param

        elif header_param and self.data_store.check_key(header_param):
            return header_param

        else:
            raise HTTPException(
                status_code=HTTP_403_FORBIDDEN, 
                detail="Wrong, revoked, or expired API key.",
            )
