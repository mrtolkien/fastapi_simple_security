from fastapi import APIRouter, Depends
import uuid

from fastapi_simple_security._security_secret import secret_based_security

api_key_router = APIRouter()


# TODO Add an environment variable to decide if it’s in docs or not


@api_key_router.get("/new", dependencies=[Depends(secret_based_security)])
def get_new_api_key() -> str:
    """
    Returns:
        api_key: a newly generated API key
    """
    # TODO Add API key to sqlite db with creation date

    return str(uuid.uuid4())


@api_key_router.get("/revoke", dependencies=[Depends(secret_based_security)])
def revoke_api_key(api_key: str):
    """
    Revokes the usage of the given API key. Does not remove its logs.

    Args:
        api_key: the api_key to revoke

    Return:
        Status 200 on successful revocation

    Raises:
        Status 404 if the API key was not in the database
    """
    return api_key


@api_key_router.get("/logs", dependencies=[Depends(secret_based_security)])
def get_api_key_usage_logs():
    # TODO Get usage logs per api key
    pass
