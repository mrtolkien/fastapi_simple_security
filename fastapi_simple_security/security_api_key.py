from fastapi import Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN

API_KEY_NAME = "access_token"

api_key_query = APIKeyQuery(name=API_KEY_NAME, scheme_name="API key query", auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, scheme_name="API key header", auto_error=False)


async def api_key_security(
    query_param: str = Security(api_key_query), header_param: str = Security(api_key_header),
):
    # TODO API key testing logic here
    if query_param == "12345":
        return query_param
    elif header_param == "12345":
        return header_param
    else:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials")
