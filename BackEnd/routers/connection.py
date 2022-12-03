import json
import uuid
from typing import Any, List
from dataclasses import dataclass

from requests import post
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel

from shared import cache


class BodyModel(BaseModel):
    claims: List[str]


router = APIRouter(
    prefix="/connection",
    tags=["connection"],
    responses={404: {"description": "can not connect"}}
)


@router.post("/")
async def create_connection(body: BodyModel):
    token = uuid.uuid1().hex
    res = post("http://localhost:8080/connection/invitation", headers={"accept": "application/json"}).json()

    if not ("invitationUrl" in res and "connectionId" in res):
        raise HTTPException(status_code=500, detail="Could not create connection")

    cache[token] = {"connectionId": res["connectionId"], "claims": body.claims}

    return {"invitationUrl": res["invitationUrl"], "token": token}


@router.get("/cache")
async def get_cache():
    return json.dumps(dict(cache.items()))



