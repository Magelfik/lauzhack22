from fastapi import APIRouter, Query, WebSocket, status, WebSocketDisconnect
from expiring_dict import ExpiringDict
from requests import get, post
from typing import List
from time import sleep

from shared import DEFAULT_CREDENTIAL_VERIF, DEFAULT_PAUSE_TIME, DEFAULT_TIMEOUT

router = APIRouter(
    prefix="/verification",
    tags=["verification"],
    responses={404: {"description": "can not connect"}}
)


async def check_verification_status(websocket: WebSocket, token: str, cache: ExpiringDict):
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
                         "credentialDefinitionId": DEFAULT_CREDENTIAL_VERIF,
                         "attributes": data["claims"]}
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
        else:
            await websocket.send_json({"status": "verification passed"})
            claims = get(
                f"http://localhost:8081/verify/process/{process_id}/claims").json()
            await websocket.send_json(claims)
