"""Sample app client used for testing.
"""
from fastapi import Depends, FastAPI

import fastapi_simple_security

app = FastAPI()


@app.get("/unsecured")
async def unsecured_endpoint():
    return {"message": "This is an unsecured endpoint"}


@app.get("/secure", dependencies=[Depends(fastapi_simple_security.api_key_security)])
async def secure_endpoint():
    return {"message": "This is a secure endpoint"}


app.include_router(
    fastapi_simple_security.api_key_router, prefix="/auth", tags=["_auth"]
)
