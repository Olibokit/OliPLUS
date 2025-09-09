import os
import uuid
from datetime import datetime
from typing import List as PyList, Optional

from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
import yaml

# 📦 Modèles ORM / Dataclasses cockpit
from OliPLUS.OliPLUS.oli_db_models import get_db, OliDocORM, OliDocTypeORM, OliMetaTypeORM, OliDocMetadataORM
from OliPLUS.OliPLUS.oliplus_models import OliDoc, OliDocType, OliMetaType, OliDocMetadata

# ✅ Initialisation cockpit API
api_app = FastAPI(
    title="OliPLUS API Cockpit",
    description="Interface REST cockpit typée et sécurisée",
    version="1.1.0"
)

# ✅ Chargement config CORS cockpitifiée
with open("cockpit_deploy/config_cors.yaml", encoding="utf-8") as f:
    cors_config = yaml.safe_load(f)["cors"]

api_app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_config["allow_origins"],
    allow_credentials=cors_config["allow_credentials"],
    allow_methods=cors_config["allow_methods"],
    allow_headers=cors_config["allow_headers"],
)

# 🔐 Authentification cockpit
security = HTTPBearer(auto_error=False)
ALLOWED_TOKENS = {"secret-token"}  # À personnaliser
ENABLE_JWT = os.getenv("OLIPLUS_JWT", "0") == "1"

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not ENABLE_JWT:
        return
    token = credentials.credentials if credentials else ""
    if token not in ALLOWED_TOKENS:
        raise HTTPException(status_code=401, detail="Token cockpit invalide")

# 🧩 Schemas cockpit
class DocStat(BaseModel):
    type: str
    nb_documents: int

class IngestPayload(BaseModel):
    document: OliDoc = Field(..., description="Document à ingérer")

# 🧠 ROUTES cockpit

## 🔧 Système
@api_app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@api_app.get("/me", tags=["System"])
def get_identity(auth: None = Depends(verify_token)):
    return {"token": "valide", "roles": ["cockpit"]}

## 📄 Documents
@api_app.get("/doc-types/", response_model=PyList[OliDocType], tags=["Documents"])
def list_doc_types(db: Session = Depends(get_db), auth: None = Depends(verify_token)):
    return [d.to_dataclass() for d in db.query(OliDocTypeORM).all()]

@api_app.get("/docs/", response_model=PyList[OliDoc], tags=["Documents"])
def list_docs(
    db: Session = Depends(get_db),
    auth: None = Depends(verify_token),
    type_id: Optional[int] = Query(None, description="Filtrer par ID de type de document"),
    statut: Optional[str] = Query(None, description="Filtrer par statut du document"),
    created_after: Optional[datetime] = Query(None, description="Documents créés après cette date (ISO)"),
    created_before: Optional[datetime] = Query(None, description="Documents créés avant cette date (ISO)")
):
    query = db.query(OliDocORM).options(
        joinedload(OliDocORM.doc_type_rel),
        joinedload(OliDocORM.metadata_rel).joinedload(OliDocMetadataORM.metadata_type_rel)
    )

    filters = []
    if type_id:
        filters.append(OliDocORM.doc_type_id == type_id)
    if statut:
        filters.append(OliDocORM.statut == statut)
    if created_after:
        filters.append(OliDocORM.created_at >= created_after)
    if created_before:
        filters.append(OliDocORM.created_at <= created_before)

    if filters:
        query = query.filter(and_(*filters))

    docs = query.all()
    return [d.to_dataclass() for d in docs]

@api_app.get("/docs/{uuid_str}", response_model=OliDoc, tags=["Documents"])
def get_doc(uuid_str: str, db: Session = Depends(get_db), auth: None = Depends(verify_token)):
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    doc = db.query(OliDocORM).filter_by(uuid=uuid_str).options(
        joinedload(OliDocORM.doc_type_rel),
        joinedload(OliDocORM.metadata_rel).joinedload(OliDocMetadataORM.metadata_type_rel)
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document introuvable")
    return doc.to_dataclass()

@api_app.post("/docs/", response_model=OliDoc, status_code=status.HTTP_201_CREATED, tags=["Documents"])
def create_doc(payload: IngestPayload, db: Session = Depends(get_db), auth: None = Depends(verify_token)):
    doc_data = payload.document
    doc = OliDocORM(
        uuid=doc_data.uuid or str(uuid.uuid4()),
        nom=doc_data.nom,
        description=doc_data.description,
        chemin_fichier=doc_data.chemin_fichier,
        statut="importé",
        created_at=doc_data.created_at,
        updated_at=doc_data.updated_at
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc.to_dataclass()

## 📊 Statistiques
@api_app.get("/stats", response_model=PyList[DocStat], tags=["Stats"])
def get_stats(db: Session = Depends(get_db), auth: None = Depends(verify_token)):
    rows = db.query(OliDocTypeORM.nom, func.count(OliDocORM.id)) \
        .join(OliDocORM, OliDocORM.doc_type_id == OliDocTypeORM.id) \
        .group_by(OliDocTypeORM.nom).all()
    return [{"type": nom, "nb_documents": count} for nom, count in rows]

## 🧬 Métadonnées
@api_app.get("/meta-types/", response_model=PyList[OliMetaType], tags=["Metadata"])
def list_meta_types(db: Session = Depends(get_db), auth: None = Depends(verify_token)):
    return [m.to_dataclass() for m in db.query(OliMetaTypeORM).all()]

@api_app.get("/metadata/", response_model=PyList[OliDocMetadata], tags=["Metadata"])
def list_metadata(db: Session = Depends(get_db), auth: None = Depends(verify_token)):
    data = db.query(OliDocMetadataORM).options(
        joinedload(OliDocMetadataORM.document_rel),
        joinedload(OliDocMetadataORM.metadata_type_rel)
    ).all()
    return [m.to_dataclass() for m in data]
