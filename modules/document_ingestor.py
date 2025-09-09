import os
from pathlib import Path
from typing import Union, Dict
import fitz  # PyMuPDF
import yaml
from pydantic import BaseModel, ValidationError
from modules.exceptions import DocumentUploadError, OCRProcessingFailure, PermissionDeniedError
from modules.permissions import has_permission_to_upload
import logging

logger = logging.getLogger("document_ingestor")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class DocumentMetadata(BaseModel):
    title: str
    author: str
    source: str
    statut_cockpit: str
    document_type: str


def extract_text_from_pdf(pdf_path: Path) -> str:
    """📄 Extrait le texte OCR d’un PDF via PyMuPDF."""
    try:
        doc = fitz.open(pdf_path)
        return "\n".join(page.get_text() for page in doc)
    except Exception as e:
        raise OCRProcessingFailure(f"OCR failed on {pdf_path.name}: {e}")


def archive_document(meta: DocumentMetadata, content: str) -> Path:
    """📦 Archive le contenu et les métadonnées dans .cockpit-archive."""
    safe_name = meta.title.replace(" ", "_").replace("/", "_")
    destination = Path(".cockpit-archive") / safe_name
    destination.mkdir(parents=True, exist_ok=True)

    # Texte brut
    (destination / "content.txt").write_text(content, encoding="utf-8")

    # Métadonnées JSON
    (destination / "metadata.json").write_text(meta.model_dump_json(indent=2), encoding="utf-8")

    # Métadonnées Markdown
    md = f"# 📘 {meta.title}\n\n"
    md += f"- **Auteur** : {meta.author}\n"
    md += f"- **Source** : {meta.source}\n"
    md += f"- **Statut cockpit** : {meta.statut_cockpit}\n"
    md += f"- **Type** : {meta.document_type}\n"
    (destination / "metadata.md").write_text(md, encoding="utf-8")

    # Métadonnées YAML
    with (destination / "metadata.yaml").open("w", encoding="utf-8") as f:
        yaml.dump(meta.model_dump(), f, sort_keys=False, allow_unicode=True)

    logger.info(f"📦 Document archivé dans {destination.resolve()}")
    return destination


def upload_and_parse_document(user: str, pdf_path: Union[str, Path], metadata: Dict) -> str:
    """🚀 Pipeline complet d’ingestion cockpit."""
    pdf_path = Path(pdf_path)

    try:
        meta = DocumentMetadata(**metadata)
    except ValidationError as ve:
        raise DocumentUploadError(f"Metadata validation failed: {ve}")

    if not has_permission_to_upload(user, metadata):
        raise PermissionDeniedError(f"User '{user}' lacks permission to upload '{meta.title}'.")

    if not pdf_path.exists():
        raise DocumentUploadError(f"PDF file not found: {pdf_path}")

    text_content = extract_text_from_pdf(pdf_path)
    archive_document(meta, text_content)

    logger.info(f"✅ Document « {meta.title} » uploaded and cockpitified.")
    return f"✅ Document « {meta.title} » uploaded and cockpitified."
