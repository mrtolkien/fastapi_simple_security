import os
import uuid
import warnings

from fastapi import Security
from fastapi.security import APIKeyHeader
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

try:
    SECRET = os.environ["FASTAPI_SIMPLE_SECURITY_SECRET"]
except KeyError:
    SECRET = str(uuid.uuid4())

    warnings.warn(
        f"ENVIRONMENT VARIABLE 'FASTAPI_SIMPLE_SECURITY_SECRET' NOT FOUND\n"
        f"\tGenerated a single-use secret key for this session:\n"
        f"\t{SECRET=}"
    )

SECRET_KEY_NAME = "secret_key"

secret_header = APIKeyHeader(name=SECRET_KEY_NAME, scheme_name="Secret header", auto_error=False)


async def secret_based_security(header_param: str = Security(secret_header)):
    """
    Args:
        header_param: parsed header field secret_header

    Returns:
        True if the authentication was successful

    Raises:
        HTTPException if the authentication failed
    """

    if header_param == SECRET:
        return True
    if not header_param:
        error = "secret_key must be passed as a header field"
    else:
        error = (
            "Wrong secret key. If not set through environment variable 'FASTAPI_SIMPLE_SECURITY_SECRET', it was "
            "generated automatically at startup and appears in the server logs."
        )

    raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail=error)
