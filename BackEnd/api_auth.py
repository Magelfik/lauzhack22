import json

from fastapi import FastAPI, Depends
from typing import List
from shared import cache

from routers import connection, test_route

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:2:e-id:1.0"
DEFAULT_ATTRIBUTES: List[str] = ["birth"]


app = FastAPI(debug=True)

app.include_router(connection.router)
app.include_router(test_route.router)


@app.get("/")
def get_root():
    return {"message": "get rekt n00b", "cache": json.dumps(dict(cache.items()))}
