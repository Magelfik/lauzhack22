from fastapi import FastAPI, Query, WebSocket, WebSocketException, status
from expiring_dict import ExpiringDict
from requests import get, post
from typing import Union

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:3:CL:63828:e-id"
DEFAULT_ATTRIBUTES: List[str] = ["birth"]


async def check_verification_status(websocket: WebSocket, token: str, cache: ExpiringDict):
    connection_id: str = cache.pop(token, "")
    if connection_id == "":
        raise WebSocketException(code=status.WS_1002_PROTOCOL_ERROR)
    await websocket.accept()
    req = "created"
    while req != "responded":
        req = get(
            f"http://localhost:8080/connection/{connection_id}").json()
    websocket.send_json({"status": "connexion established with client"})
    payload: dict = {"connectionId": connection_id,
                     "credentialDefinitionId": DEFAULT_CREDENTIAL_VERIF,
                     "attributes": DEFAULT_ATTRIBUTES}
    req = post("http://localhost:8081/verify/process", json=payload).json()
    process_id: str = req["processId"]
    req = req["status"]
    while req != "VERIFIED":
        req = get(
            f"http://localhost:8081/verify/process/{process_id}/state").json()
    claims = get(
        f"http://localhost:8081/verify/process/{process_id}/claims")
    websocket.send_text(claims)
    websocket.close()
