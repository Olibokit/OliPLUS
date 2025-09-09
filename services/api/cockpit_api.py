from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from modules.document_ingestor import upload_and_parse_document
from modules.permissions import has_permission_to_upload, has_permission_to_read
import yaml, os, tempfile, logging

# 🔧 Logger
logger = logging.getLogger("cockpit_api")
logger.setLevel(logging.INFO)
handler = logging.FileHandler("logs/api.log")
logger.addHandler(handler)

# ⚙️ Config CORS dynamique
ALLOWED_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app = FastAPI(title="Cockpit API", version="1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 🧪 Endpoint de test
@app.get("/ping", summary="Ping", description="Test de disponibilité de l'API")
def ping():
    return {"message": "pong 🏓"}

# 📥 Endpoint d’upload PDF
@app.post("/upload-pdf", summary="Upload PDF", description="Uploader un document avec métadonnées")
async def upload_pdf(
    user: str = Form(...),
    title: str = Form(...),
    author: str = Form(...),
    source: str = Form(...),
    statut_cockpit: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...)
):
    metadata = {
        "title": title,
        "author": author,
        "source": source,
        "statut_cockpit": statut_cockpit,
        "document_type": document_type
    }

    # 🔐 Permissions
    if not has_permission_to_upload(user, metadata):
        logger.warning(f"Upload refusé pour {user}")
        raise HTTPException(status_code=403, detail=f"Utilisateur '{user}' non autorisé à uploader.")

    # 📄 Validation du fichier
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont autorisés.")

    # 📂 Sauvegarde temporaire
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        pdf_path = Path(tmp.name)

    # 🧠 Traitement
    try:
        message = upload_and_parse_document(user, pdf_path, metadata)
        logger.info(f"Upload réussi : {file.filename} par {user}")
        return {"status": "success", "message": message}
    except Exception as e:
        logger.error(f"Erreur upload : {e}")
        raise HTTPException(status_code=400, detail=str(e))

# 📦 Endpoint pour consulter les métadonnées archivées
@app.get("/archive/{title}", summary="Lire archive", description="Consulter les métadonnées archivées d’un document")
def get_archived_metadata(title: str, user: str = "invite"):
    if not has_permission_to_read(user):
        logger.warning(f"Lecture refusée pour {user}")
        raise HTTPException(status_code=403, detail=f"Utilisateur '{user}' non autorisé à lire les archives.")

    safe_name = title.replace(" ", "_").replace("/", "_")
    archive_path = Path(".cockpit-archive") / safe_name

    if not archive_path.exists():
        raise HTTPException(status_code=404, detail="Document non archivé")

    try:
        with open(archive_path / "metadata.yaml", "r", encoding="utf-8") as f:
            metadata = yaml.safe_load(f)
        return {"title": title, "metadata": metadata}
    except Exception as e:
        logger.error(f"Erreur lecture YAML : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur lecture YAML : {e}")
