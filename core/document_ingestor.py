import json
import logging
from pathlib import Path
from typing import List, Dict, Optional

from OliPLUS.OliPLUS.oliplus_models import (
    OliDoc, OliDocMetadata, OliDocType,
    OliMetaType
)

logger = logging.getLogger("cockpit.import")
logger.setLevel(logging.INFO)

def load_json(path: Path) -> List[dict]:
    """
    📥 Charge un fichier JSON contenant une liste de documents ou de métadonnées.
    """
    if not path.exists():
        raise FileNotFoundError(f"🚫 Fichier non trouvé : {path}")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"⚠️ Format inattendu dans {path.name} (attendu : liste)")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erreur JSON dans {path.name} : {e}")
        raise

def build_doc_type(entry: dict) -> Optional[OliDocType]:
    """
    🧩 Construit un type documentaire à partir d'une entrée JSON.
    """
    dt = entry.get("document_type")
    if not dt:
        return None
    return OliDocType(
        nom=dt.get("label", ""),
        uuid=dt.get("uuid")
    )

def import_olidocs(data: List[dict]) -> List[OliDoc]:
    """
    📄 Construit une liste d'objets OliDoc à partir d'une structure JSON externe.
    """
    docs: List[OliDoc] = []
    for entry in data:
        if not entry.get("id") or not entry.get("label"):
            logger.warning(f"⚠️ Document ignoré : entrée incomplète {entry}")
            continue

        doc = OliDoc(
            id=entry["id"],
            nom=entry["label"],
            uuid=entry.get("uuid"),
            created_at=entry.get("datetime_created"),
            updated_at=entry.get("datetime_modified"),
            doc_type=build_doc_type(entry)
        )
        docs.append(doc)

    logger.info(f"📄 {len(docs)} documents importés depuis JSON.")
    return docs

def import_metadata(
    data: List[dict],
    doc_by_id: Dict[int, OliDoc],
    types_by_id: Dict[int, OliMetaType]
) -> List[OliDocMetadata]:
    """
    🧩 Associe des métadonnées à des documents existants à partir d'un JSON.
    """
    metadata: List[OliDocMetadata] = []
    for item in data:
        doc_id = item.get("document_id")
        type_id = item.get("metadata_type_id")
        valeur = item.get("value")

        if not doc_id or not type_id or valeur is None:
            logger.warning(f"⚠️ Métadonnée ignorée : données incomplètes {item}")
            continue

        doc = doc_by_id.get(doc_id)
        meta_type = types_by_id.get(type_id)

        if doc and meta_type:
            m = OliDocMetadata(
                document=doc,
                metadata_type=meta_type,
                valeur=valeur
            )
            metadata.append(m)
        else:
            logger.warning(f"⚠️ Métadonnée ignorée : doc_id={doc_id}, meta_type_id={type_id}")

    logger.info(f"🧩 {len(metadata)} métadonnées associées.")
    return metadata
