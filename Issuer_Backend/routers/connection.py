import json
import uuid
from typing import List
from dataclasses import dataclass

from requests import post, get
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from shared import cache, IDENTITY_CREDENTIAL_ID


class BodyModel(BaseModel):
    claims: List[str]


router = APIRouter(
    prefix="/connection",
    tags=["connection"],
    responses={404: {"description": "can not connect"}}
)


def create_connection_for_issuer():
    res = post("http://localhost:8080/connection/invitation", headers={"accept": "application/json"}).json()
    if not ("invitationUrl" in res and "connectionId" in res):
        raise HTTPException(status_code=500, detail="Could not create connection")
    return res


@router.post("/")
async def create_connection(body: BodyModel):
    schemas = get("http://localhost:8100/issue/credentials/definitions", headers={"accept": "application/json"}).json()
    cred_def_ids = [schema["credentialDefinitionId"] for schema in schemas]
    if IDENTITY_CREDENTIAL_ID not in cred_def_ids:
        raise HTTPException(status_code=400, detail="API schema not in trusted schema IDs. See your service provider to solve the problem.")

    schema_claims = [s for s in schemas if s["credentialDefinitionId"] == IDENTITY_CREDENTIAL_ID][0]["claims"]

    claims = body.claims
    for claim in claims:
        if claim not in schema_claims:
            raise HTTPException(status_code=400, detail="Invalid claim for this schema.")

    token = uuid.uuid1().hex
    res = post("http://localhost:8080/connection/invitation", headers={"accept": "application/json"}).json()

    if not ("invitationUrl" in res and "connectionId" in res):
        raise HTTPException(status_code=500, detail="Could not create connection")

    cache[token] = {"connectionId": res["connectionId"], "claims": claims}

    return {"invitationUrl": res["invitationUrl"], "token": token}


@router.get("/cache")
async def get_cache():
    return json.dumps(dict(cache.items()))



