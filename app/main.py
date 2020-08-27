from fastapi import FastAPI, Depends
import fastapi_simple_security


app = FastAPI(title="FastAPI simple security", version="test")


@app.get("/open")
async def root():
    return {"message": "This is an unsecured endpoint"}


@app.get("/secure", dependencies=[Depends(fastapi_simple_security.api_key_security)])
async def root():
    return {"message": "This is a secured endpoint"}


app.include_router(fastapi_simple_security.api_key_router, prefix="/auth", tags=["_auth"])
