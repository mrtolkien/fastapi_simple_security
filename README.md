# fastapi_simple_security
API key based security package for FastAPI, focused on simplicity of use:
- Full functionality out of the box with no additional configuration required
- Single-function API key security with local `sqlite` backend, working with both header and query parameters
- Automatic key creation, revoking, and usage logs through administrator endpoints

# Installation
`pip install fastapi_simple_security`

This package depends only on fastapi and the python standard library.

# Usage

## Application
Example code to secure an endpoint and add `/auth/` endpoints to manage API keys:
```python
import fastapi_simple_security
from fastapi import Depends, FastAPI

app = FastAPI()

app.include_router(fastapi_simple_security.api_key_router, prefix="/auth", tags=["_auth"])

@app.get("/secure_endpoint", dependencies=[Depends(fastapi_simple_security.api_key_security)])
async def root():
    return {"message": "This is a secured endpoint"} 
```

## API key creation through docs

Go to `/docs` on your API and inform your secret key. All the administrator endpoints only support header security to 
make sure the secret key is not inadvertently shared when sharing an URL:
![secret_header](images/secret_header.png)

Then, you can use `/auth/new` to generate a new API key. If you set `never_expire`, the key will not be expired
automatically:
![secret_header](images/new_api_key.png)

You can of course automate API key acquisition through python if you prefer to by using the endpoints directly. If you
decide to do so, you can hide the functions from the doc with the environment variable 
`FASTAPI_SIMPLE_SECURITY_HIDE_DOCS`.

# Configuration and persistence
Environment variables:
- `FASTAPI_SIMPLE_SECURITY_SECRET`: the master key for the admin. Allows generation of new API keys, revoking of
 existing ones, and API key usage viewing.
- `FASTAPI_SIMPLE_SECURITY_HIDE_DOCS`: if set, the API key management endpoints will not appear in the documentation.
- `FAST_API_SIMPLE_SECURITY_AUTOMATIC_EXPIRATION`: how many days until an API key is considered automatically expired.
Defaults to 15 days.
- `FASTAPI_SIMPLE_SECURITY_DB_LOCATION`: the location of the local sqlite database file. /app/sqlite.db by default. When
running the app inside Docker you can use a bind mount for persistence.

# Contributing
The attached docker image runs a test app on `localhost:8080` with secret key `TEST_SECRET`. Run it with:
```shell script
docker-compose build && docker-compose up -d
```

Currently wanted contributions are:
- Unit tests
- More options with sensible defaults
- Full per-API key logging options
- Offering more back-end options for api keys storage
