from fastapi import FastAPI, WebSocket, Query, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import requests
from uuid import uuid1
from pyhanko.sign.fields import SigFieldSpec, append_signature_field
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter
from pyhanko.sign import signers

app = FastAPI(debug=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

cms_signer = signers.SimpleSigner.load(
    './key.pem', 'cert.pem',
    key_passphrase=b'Super'
)


@app.get("/")
def get_root():
    return {"message": "get rekt n00b"}


@app.websocket("/obtain/attestation")
async def websocket_attestation(websocket: WebSocket):
    await websocket.accept()
    data: dict = await websocket.receive_json()
    response = requests.get(
        f"http://hackademia.test/pouet?first_name={data['first_name']}&last_name={data['last_name']}&birth={data['birth']}")
    filename: str = uuid1().hex
    with open(f"tmp/{filename}_unsigned.pdf", "wb") as f:
        f.write(response.content)

    payload: bytes = b''
    with open(f"tmp/{filename}_unsigned.pdf", 'rb+') as doc:
        w = IncrementalPdfFileWriter(doc)
        append_signature_field(w, SigFieldSpec(
            sig_field_name="Signature", on_page=0, box=(0, 0, 595, 500)))
        w.write_in_place()
        with open(f"tmp/{filename}_signed.pdf", 'wb') as out_doc:
            await signers.async_sign_pdf(
                w, signers.PdfSignatureMetadata(field_name='Signature'),
                signer=cms_signer, output=out_doc
            )

    with open(f"tmp/{filename}_signed.pdf", 'rb') as signed:
        payload = signed.read()
    await websocket.send_bytes(payload)
