from fastapi import APIRouter, Query, WebSocket, WebSocketException, status
from expiring_dict import ExpiringDict
from requests import get, post
from typing import List

from shared import cache

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:3:CL:63828:e-id"
DEFAULT_ATTRIBUTES: List[str] = ["birth"]

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
    while req != "responded":
        req = get(
            f"http://localhost:8080/connection/{data['connectionId']}").json()
    await websocket.send_json({"status": "connexion established with client"})
    payload: dict = {"connectionId": data['connectionId'],
                     "credentialDefinitionId": DEFAULT_CREDENTIAL_VERIF,
                     "attributes": data["claims"]}
    req = post("http://localhost:8081/verify/process", json=payload).json()
    process_id: str = req["processId"]
    req = req["status"]
    while req != "VERIFIED":
        req = get(
            f"http://localhost:8081/verify/process/{process_id}/state").json()
    claims = get(
        f"http://localhost:8081/verify/process/{process_id}/claims").json()
    print(f"coucou {claims}")
    await websocket.send_json(claims)



