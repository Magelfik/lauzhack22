import json
import uuid

from requests import get, post
from fastapi import FastAPI


app = FastAPI(debug=True)


@app.get("/invitation")
def get_invitation():
    token = uuid.uuid1()
    res = json.loads(post("localhost:8080/connection/invitation").json())


@app.get("/verify/")
def verify():
    pass


