import json

from fastapi import FastAPI, WebSocket, Query

from starlette.middleware.cors import CORSMiddleware

from routers.status import check_verification_status
from shared import cache, NULL_UUID

from routers import connection, test_route

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connection.router)
app.include_router(test_route.router)


@app.get("/")
def get_root():
    return {"message": "get rekt n00b", "cache": json.dumps(dict(cache.items()))}


@app.websocket("/{token}/status")
async def websocket_verification(websocket: WebSocket, token: str = Query(default=NULL_UUID, min_length=32, max_length=32)):
    await check_verification_status(websocket, token, cache)
