import json
import uuid

from requests import get, post
from fastapi import FastAPI, Query, WebSocket
from typing import List
from expiring_dict import ExpiringDict
from dataclasses import dataclass
from status import check_verification_status

NULL_UUID: str = "00000000000000000000000000000000"
DEFAULT_CREDENTIAL_VERIF: str = "4HS52UpbxN8rHqCHWgtCSN:2:e-id:1.0"
DEFAULT_ATTRIBUTES: List[str] = ["birth"]
cache: ExpiringDict(600)


@dataclass
class AgeVerificationRequest():
    connection_id: str
    process_id: str
    claims_ready: bool


app = FastAPI(debug=True)


@app.get("/verification/request/")
async def get_verif_request():
    token = uuid.uuid1()
    res = json.loads(post("localhost:8080/connection/invitation").json())


@app.websocket("/ws/verification/{token}/status")
async def websocket_verification(websocket: WebSocket, token: str = Query(default=NULL_UUID, min_length=32, max_length=32)):
    await check_verification_status(websocket, token, cache)
