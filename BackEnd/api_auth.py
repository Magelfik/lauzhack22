import json
import uuid

from requests import get, post
from fastapi import FastAPI, Query

NULL_UUID: str = "00000000000000000000000000000000"

app = FastAPI(debug=True)


@app.get("/verification/request/")
def get_verif_request():
    token = uuid.uuid1()
    res = json.loads(post("localhost:8080/connection/invitation").json())


@app.get("/verification/status/")
def get_verif_status(token: str = Query(default=NULL_UUID, min_length=32, max_length=32)):
    pass
