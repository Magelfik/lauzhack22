import json
import uuid
from typing import Any
from dataclasses import dataclass

from requests import post
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api_auth import cache


class ConnectionItem(BaseModel):
    invitation_url: str
    token: str

    def __init__(self, invitation_url: str, token: str, **data: Any):
        super().__init__(**data)
        self.invitation_url = invitation_url
        self.token = token


@dataclass
class ConnectionStatusItem(BaseModel):
    pass


router = APIRouter(
    prefix="/connection",
    responses={404: {"description": "can not connect"}}
)


@router.get("/", response_model=ConnectionItem)
def create_connection():
    token = uuid.uuid1().hex
    res = json.loads(post("localhost:8080/connection/invitation").json())

    if not ("invitationUrl" in res and "connectionId" in res):
        raise HTTPException(status_code=500, detail="Could not create connection")

    cache[token] = res["connectionId"]

    return ConnectionItem(res["invitationUrl"], token)






