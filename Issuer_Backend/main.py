import json
from time import sleep

from expiring_dict import ExpiringDict
from fastapi import FastAPI, WebSocket, Query, WebSocketDisconnect, status, HTTPException
from requests import get, post

from starlette.middleware.cors import CORSMiddleware

from forge.schema_definition_forger import forge
from routers import connection
from routers.connection import create_connection_for_issuer
from shared import DEFAULT_TIMEOUT, DEFAULT_PAUSE_TIME, cache, NULL_UUID, IDENTITY_CREDENTIAL_ID, \
    INSURANCE_CREDENTIAL_ID

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(connection.router)


@app.get("/")
def get_root():
    return {"message": "get rekt n00b", "cache": json.dumps(dict(cache.items()))}


async def wait_process(websocket: WebSocket, payload: dict):
    req = post("http://localhost:8081/verify/process", json=payload).json()
    process_id: str = req["processId"]
    req = req["status"]
    i = 0
    while req != "VERIFIED" and i < DEFAULT_TIMEOUT:
        sleep(DEFAULT_PAUSE_TIME)
        req = get(
            f"http://localhost:8081/verify/process/{process_id}/state").json()
        i += 1
    if i >= DEFAULT_TIMEOUT:
        await websocket.send_json({"error": "timeout"})
        raise WebSocketDisconnect(code=status.WS_1002_PROTOCOL_ERROR, reason="Timeout")
    await websocket.send_json({"status": "verification passed"})
    return process_id


async def process_connection(websocket: WebSocket, token: str, cache: ExpiringDict):
    data: dict = cache.pop(token, {})
    await websocket.accept()
    if data == {}:
        raise WebSocketDisconnect(code=status.WS_1002_PROTOCOL_ERROR, reason="Invalid token for authentication")
    req = "created"
    i = 0
    while req != "responded" and i < DEFAULT_TIMEOUT:
        sleep(DEFAULT_PAUSE_TIME)
        req = get(
            f"http://localhost:8080/connection/{data['connectionId']}").json()
        i += 1
    if i >= DEFAULT_TIMEOUT:
        await websocket.send_json({{"error": "timeout"}})
    else:
        await websocket.send_json({"status": "connexion established with client"})
        payload: dict = {"connectionId": data['connectionId'],
                         "credentialDefinitionId": IDENTITY_CREDENTIAL_ID,
                         "attributes": data["claims"]}

        process_id = await wait_process(websocket, payload)
        claims = get(
            f"http://localhost:8081/verify/process/{process_id}/claims").json()

        attributes: dict = forge(claims)
        payload: dict = {
            "connectionId": data['connectionId'],
            "credentialDefinitionId": INSURANCE_CREDENTIAL_ID,
            "attributes": attributes,
        }

        res = post("http://localhost:8100/issue/process", headers={"accept": "application/json", "content-type": "application/json"}, json=payload).json()
        await websocket.send_json({"status": "Identity submitted"})

        if "errorCode" in res:
            raise WebSocketDisconnect(code=status.WS_1002_PROTOCOL_ERROR, reason="Could not forge new identity")


@app.websocket("/{token}/status")
async def websocket_verification(websocket: WebSocket, token: str = Query(default=NULL_UUID, min_length=32, max_length=32)):
    try:
        await process_connection(websocket, token, cache)
    except WebSocketDisconnect as wsds:
        await websocket.close(wsds.code, wsds.reason)