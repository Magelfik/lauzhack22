import json
import uuid

from requests import get, post
from fastapi import FastAPI, Query, WebSocket
from typing import List
from expiring_dict import ExpiringDict
from dataclasses import dataclass

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:2:e-id:1.0"
DEFAULT_ATTRIBUTES: List[str] = ["birth"]
cache: ExpiringDict(600)


@dataclass
class AgeVerificationRequest():
    connection_id: str
    process_id: str
    age_verified: bool


app = FastAPI(debug=True)


@app.get("/verification/request/")
async def get_verif_request():
    token = uuid.uuid1()
    res = json.loads(post("localhost:8080/connection/invitation").json())


@app.websocket("/ws/verification/{token}/status")
async def websocket_verification(websocket: WebSocket, token: str = Query(default=NULL_UUID, min_length=32, max_length=32)):
    await websocket.accept()
    while True:

        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")
    #cache.get(token, {})
    payload: dict = {"connectionId": NULL_UUID,
                     "credentialDefinitionId": DEFAULT_CREDENTIAL_VERIF,
                     "attributes": DEFAULT_ATTRIBUTES}
    res = post("http://localhost:8081/verify/process", json=payload)
    # recover process id
