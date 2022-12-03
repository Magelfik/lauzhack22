from expiring_dict import ExpiringDict


def check_verification_status(websocket: WebSocket, token: str, cache: ExpiringDict):
    if not token in cache.keys():

        pass
    # await websocket.accept()

    # data = await websocket.receive_text()
    # await websocket.send_text(f"Message text was: {data}")
    #cache.get(token, {})
    # payload: dict = {"connectionId": NULL_UUID,
    #                 "credentialDefinitionId": DEFAULT_CREDENTIAL_VERIF,
    #                 "attributes": DEFAULT_ATTRIBUTES}
    #res = post("http://localhost:8081/verify/process", json=payload)
    # recover process id
