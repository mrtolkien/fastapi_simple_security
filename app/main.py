"""Sample app client used for testing.
"""
from fastapi import Depends, FastAPI

from fastapi_sqlmodel_security import create_auth_router, ApiKeySecurity, NoAuthApiKeySecurity, SqlModelDataStore

app = FastAPI()

db_location = "keys.db"

data_store = SqlModelDataStore(conn_url=f"sqlite:///{db_location}")


@app.get("/unsecured")
async def unsecured_endpoint():
    return {"message": "This is an unsecured endpoint"}


@app.get("/secure", dependencies=[Depends(ApiKeySecurity(data_store))])
async def secure_endpoint():
    return {"message": "This is a secure endpoint"}


@app.get("/no-auth", dependencies=[Depends(NoAuthApiKeySecurity(data_store))])
async def no_auth_endpoint():
    return {"message": "This is a no-auth endpoint"}


app.include_router(router=create_auth_router(data_store), prefix="/auth", tags=["_auth"])
