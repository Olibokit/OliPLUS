from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class OliDocType:
    id: Optional[int] = None
    uuid: Optional[str] = None
    nom: Optional[str] = None
    description: Optional[str] = None
    code_classification: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class OliMetaType:
    id: Optional[int] = None
    uuid: Optional[str] = None
    nom: Optional[str] = None
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class OliDocMetadata:
    id: Optional[int] = None
    uuid: Optional[str] = None
    document_id: Optional[int] = None
    document: Optional[OliDoc] = None
    metadata_type: Optional[OliMetaType] = None
    valeur: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class OliDocVersion:
    id: Optional[int] = None
    uuid: Optional[str] = None
    version_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class OliDocPage:
    id: Optional[int] = None
    page_number: Optional[int] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class OliDoc:
    id: Optional[int] = None
    uuid: Optional[str] = None
    nom: Optional[str] = None
    description: Optional[str] = None
    chemin_fichier: Optional[str] = None
    mimetype: Optional[str] = None
    taille_fichier: Optional[int] = None
    nombre_pages: Optional[int] = None
    checksum: Optional[str] = None
    statut: Optional[str] = None
    language: Optional[str] = None
    source_url: Optional[str] = None
    owner_id: Optional[str] = None
    doc_type: Optional[OliDocType] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: List[OliDocMetadata] = field(default_factory=list)
    versions: List[OliDocVersion] = field(default_factory=list)
    pages: List[OliDocPage] = field(default_factory=list)
