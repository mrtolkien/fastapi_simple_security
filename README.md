# fastapi_simple_security
API-key based security package for FastAPI, focused on simplicity of use

# Installation
`pip install fastapi_simple_security`

This package depends only on fastapi and the python standard library.

# Usage

Example code to secure an endpoint and add endpoints to manage API keys:
```python
import fastapi_simple_security
from fastapi import Depends, FastAPI

app = FastAPI()

app.include_router(fastapi_simple_security.api_key_router, prefix="/auth", tags=["_auth"])

@app.get("/secure_endpoint", dependencies=[Depends(fastapi_simple_security.api_key_security)])
async def root():
    return {"message": "This is a secured endpoint"} 
```

# Configuration
Environment variables:
- `FASTAPI_SIMPLE_SECURITY_SECRET`: the master key for the admin. Allows generation of new API keys, revoking of
 existing ones, and API key usage viewing. 
- `FASTAPI_SIMPLE_SECURITY_DB_LOCATION`: the location of the local sqlite database file. /app/sqlite.db by default.

# Contributing
The attached docker image runs a test app on `localhost:8080`. Run it with:
```shell script
docker-compose build && docker-compose up -d
```

Currently wanted contributions are:
- Unit tests
- More options with sensible defaults
- Full per-API key logging options
- Offering more back-end options for api keys storage
