from typing import List, Optional
import os

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from fastapi_simple_security._security_secret import secret_based_security
from fastapi_simple_security._sqlite_access import sqlite_access

api_key_router = APIRouter()

show_endpoints = False if "FASTAPI_SIMPLE_SECURITY_HIDE_DOCS" in os.environ else True


@api_key_router.get("/new", dependencies=[Depends(secret_based_security)], include_in_schema=show_endpoints)
def get_new_api_key(never_expires=None) -> str:
    """
    Args:
        never_expires: if set, the created API key will never be considered expired

    Returns:
        api_key: a newly generated API key
    """
    return sqlite_access.create_key(never_expires)


@api_key_router.get("/revoke", dependencies=[Depends(secret_based_security)], include_in_schema=show_endpoints)
def revoke_api_key(api_key: str):
    """
    Revokes the usage of the given API key

    Args:
        api_key: the api_key to revoke
    """
    return sqlite_access.revoke_key(api_key)


class UsageLog(BaseModel):
    api_key: str
    is_active: bool
    never_expire: bool
    creation_date: str
    latest_query_date: Optional[str]
    total_queries: int


class UsageLogs(BaseModel):
    logs: List[UsageLog]


@api_key_router.get(
    "/logs", dependencies=[Depends(secret_based_security)], response_model=UsageLogs, include_in_schema=show_endpoints
)
def get_api_key_usage_logs():
    """
    Returns usage information for all API keys
    """
    # TODO Add some sort of filtering on older keys/unused keys?

    return UsageLogs(
        logs=[
            UsageLog(
                api_key=row[0],
                is_active=row[1],
                never_expire=row[2],
                creation_date=row[3],
                latest_query_date=row[4],
                total_queries=row[5],
            )
            for row in sqlite_access.get_usage_stats()
        ]
    )
