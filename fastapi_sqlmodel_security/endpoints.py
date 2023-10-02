"""Endpoints defined by the dependency."""
import os
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from fastapi_sqlmodel_security._models import UsageLogs
from fastapi_sqlmodel_security._security_secret import secret_based_security
from fastapi_sqlmodel_security.data_store import DataStore


def create_auth_router(data_store: DataStore) -> APIRouter:
    """Creates the API router for the API key endpoints."""
    api_key_router = APIRouter()

    show_endpoints = "FASTAPI_SQLMODEL_SECURITY_HIDE_DOCS" not in os.environ


    @api_key_router.get(
        "/new",
        dependencies=[Depends(secret_based_security)],
        include_in_schema=show_endpoints,
    )
    def get_new_api_key(
        name: str = Query(
            None,
            description="set API key name",
        ),
        never_expires: bool = Query(
            False,
            description="if set, the created API key will never be considered expired",
        ),
    ) -> str:
        """
        Returns:
            api_key: a newly generated API key
        """
        return data_store.create_key(name, never_expires)


    @api_key_router.get(
        "/revoke",
        dependencies=[Depends(secret_based_security)],
        include_in_schema=show_endpoints,
    )
    def revoke_api_key(
        api_key: str = Query(..., alias="api-key", description="the api_key to revoke")
    ) -> str:
        """
        Revokes the usage of the given API key

        """
        if data_store.revoke_key(api_key):
            return "API key revoked."
        else:
            raise HTTPException(status_code=404, detail="API key not found")


    @api_key_router.get(
        "/renew",
        dependencies=[Depends(secret_based_security)],
        include_in_schema=show_endpoints,
    )
    def renew_api_key(
        api_key: str = Query(..., alias="api-key", description="the API key to renew"),
        expiration_date: Optional[date] = Query(
            None,
            alias="expiration-date",
            description="the new expiration date in ISO 8601 format",
        ),
    ) -> str:
        """Renews the chosen API key, reactivating it if it was revoked."""
        if data_store.renew_key(api_key, expiration_date):
            return "API key renewed."
        else:
            raise HTTPException(status_code=404, detail="API key not found")



    @api_key_router.get(
        "/logs",
        dependencies=[Depends(secret_based_security)],
        response_model=UsageLogs,
        include_in_schema=show_endpoints,
    )
    def get_api_key_usage_logs() -> UsageLogs:
        """Returns usage information for all API keys."""
        # TODO Add some sort of filtering on older keys/unused keys?

        return UsageLogs(
            logs=data_store.get_usage_stats()
        )

    return api_key_router
