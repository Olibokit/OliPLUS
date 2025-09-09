from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from itsdangerous import TimestampSigner, BadSignature, SignatureExpired
import os
import time

# 🔐 Configuration
SECRET_KEY = "your-secret-key"
signer = TimestampSigner(SECRET_KEY)
EXPIRATION_SECONDS = 3600  # ⏳ 1 heure

app = FastAPI()

# ✅ Génère une URL sécurisée avec expiration
def get_file_secure_url(name: str) -> str:
    if not name:
        raise HTTPException(status_code=400, detail="Nom de fichier requis")
    token = signer.sign(name.encode()).decode()
    return f"/download?token={token}"

# 📥 Télécharge le fichier si le token est valide et non expiré
def download_file(token: str) -> StreamingResponse:
    try:
        name = signer.unsign(token, max_age=EXPIRATION_SECONDS).decode()
    except SignatureExpired:
        raise HTTPException(status_code=403, detail="Lien expiré")
    except BadSignature:
        raise HTTPException(status_code=403, detail="Lien invalide")

    file_path = os.path.join("files", name)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Fichier introuvable")

    def file_stream():
        with open(file_path, "rb") as f:
            yield from f

    return StreamingResponse(file_stream(), media_type="application/octet-stream", headers={
        "Content-Disposition": f"attachment; filename={name}"
    })

# 🚀 Endpoint FastAPI
@app.get("/download")
def secure_download(token: str = Query(...)):
    return download_file(token)
