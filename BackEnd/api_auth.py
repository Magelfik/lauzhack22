import json

from fastapi import FastAPI, WebSocket, Query
from typing import List

from routers.status import check_verification_status
from shared import cache

from routers import connection, test_route, status

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:2:e-id:1.0"
DEFAULT_ATTRIBUTES: List[str] = ["birth"]


app = FastAPI(debug=True)

app.include_router(connection.router)
app.include_router(test_route.router)


@app.get("/")
def get_root():
    return {"message": "get rekt n00b", "cache": json.dumps(dict(cache.items()))}


@app.websocket("/{token}/status")
async def websocket_verification(websocket: WebSocket, token: str = Query(default=NULL_UUID, min_length=32, max_length=32)):
    await check_verification_status(websocket, token, cache)
