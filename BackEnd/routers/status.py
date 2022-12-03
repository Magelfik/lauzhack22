from fastapi import APIRouter, Query, WebSocket, WebSocketException, status
from expiring_dict import ExpiringDict
from requests import get, post
from typing import List
from time import sleep

from shared import cache

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:3:CL:63828:e-id"
DEFAULT_ATTRIBUTES: List[str] = ["birth"]
DEFAULT_PAUSE_TIME: float = 0.1
DEFAULT_TIMEOUT: int = int(600/DEFAULT_PAUSE_TIME)  # timeout : ~600s ~ 10min


router = APIRouter(
    prefix="/verification",
    tags=["verification"],
    responses={404: {"description": "can not connect"}}
)


async def check_verification_status(websocket: WebSocket, token: str, cache: ExpiringDict):
    data: dict = cache.pop(token, {})
    if data == {}:
        raise WebSocketException(code=status.WS_1002_PROTOCOL_ERROR)
    await websocket.accept()
    req = "created"
    i = 0
    while req != "responded" and i < DEFAULT_TIMEOUT:
        sleep(DEFAULT_PAUSE_TIME)
        req = get(
            f"http://localhost:8080/connection/{data['connectionId']}").json()
        i += 1
    if i >= DEFAULT_TIMEOUT:
        await websocket.send_json({"status": "error : timeout"})
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
            await websocket.send_json({"status": "error : timeout"})
        else:
            await websocket.send_json({"status": "verification passed"})
            claims = get(
                f"http://localhost:8081/verify/process/{process_id}/claims").json()
            await websocket.send_json(claims)
