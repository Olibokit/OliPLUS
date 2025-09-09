import json
import yaml
import argparse
from pathlib import Path
from dataclasses import asdict
from typing import List, Dict, Any
import sys

from classification_service import ClassificationService
from import_service import load_json, import_olidocs, import_metadata

def filter_docs_by_doc_type_code(docs: List[Any], code_prefix: str) -> List[Any]:
    return [
        doc for doc in docs
        if doc.doc_type and getattr(doc.doc_type, "code", "").startswith(code_prefix)
    ]

def filter_and_export(
    docs_path: str,
    meta_path: str,
    yaml_path: str,
    output_path: str,
    doc_type_code: str = "8000",
    output_format: str = "json",
    debug: bool = False
) -> None:
    # 📂 Vérification des fichiers source
    docs_file = Path(docs_path)
    yaml_file = Path(yaml_path)
    meta_file = Path(meta_path)
    output_file = Path(output_path)

    if not docs_file.exists():
        print(f"❌ Fichier documents introuvable : {docs_file}")
        sys.exit(1)

    if not yaml_file.exists():
        print(f"❌ Fichier YAML de classification introuvable : {yaml_file}")
        sys.exit(1)

    # 📘 Chargement de la classification cockpit
    service = ClassificationService(yaml_file)
    service.load()
    doc_types = service.list_all_categories()
    types_by_code = {t.code: t for t in doc_types}

    # 📄 Import des documents
    docs_raw = load_json(docs_file)
    docs_all = import_olidocs(docs_raw)

    if debug:
        print("🔍 Aperçu des doc_type détectés (10 premiers) :")
        for d in docs_all[:10]:
            code = getattr(d.doc_type, 'code', '❌')
            nom = getattr(d.doc_type, 'nom', '❌')
            print(f"• {d.nom} → code: {code} | nom: {nom}")

    docs = filter_docs_by_doc_type_code(docs_all, doc_type_code)
    if not docs:
        print(f"⚠️ Aucun document trouvé avec un type commençant par : {doc_type_code}")
        sys.exit(0)

    doc_by_id = {d.id: d for d in docs}

    # 📑 Import des métadonnées si disponibles
    metadata = []
    if meta_file.exists():
        metadata_raw = load_json(meta_file)
        metadata = import_metadata(metadata_raw, doc_by_id, {})

    # 📦 Construction du payload cockpit
    export_data = {
        "doc_types": [asdict(t) for t in doc_types],
        "docs": [asdict(d) for d in docs],
        "metadata": [asdict(m) for m in metadata]
    }

    output_file.parent.mkdir(parents=True, exist_ok=True)

    # 📤 Export selon le format
    if output_format == "yaml" or output_file.suffix.lower() == ".yaml":
        with open(output_file, "w", encoding="utf-8") as f:
            yaml.dump(export_data, f, sort_keys=False, allow_unicode=True)
        format_label = "YAML"
    elif output_format == "json" or output_file.suffix.lower() == ".json":
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        format_label = "JSON"
    else:
        print(f"❌ Format de sortie non reconnu : {output_format}")
        sys.exit(1)

    print(f"\n✅ Export terminé : {len(docs)} documents & {len(metadata)} métadonnées")
    print(f"📤 Fichier généré : {output_file} ({format_label})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="📂 Filtrage ciblé des documents externes vers payload cockpit Oliplus"
    )
    parser.add_argument("--docs", dest="docs_path", default="source_documents.json",
                        help="Chemin vers le JSON des documents source")
    parser.add_argument("--meta", dest="meta_path", default="source_metadata.json",
                        help="Chemin vers le JSON des métadonnées")
    parser.add_argument("--yaml", dest="yaml_path", default="classification_structure.yaml",
                        help="Fichier YAML de classification cockpit")
    parser.add_argument("--output", dest="output_path", default="oliplus_payload_filtered.json",
                        help="Fichier de sortie (JSON/YAML)")
    parser.add_argument("--code", dest="doc_type_code", default="8000",
                        help="Filtre par préfixe du doc_type.code (ex: 8000)")
    parser.add_argument("--format", dest="output_format", choices=["json", "yaml"], default="json",
                        help="Format de sortie : json ou yaml")
    parser.add_argument("--debug", action="store_true",
                        help="Affiche un aperçu des types détectés dans les 10 premiers documents")

    args = parser.parse_args()

    filter_and_export(
        docs_path=args.docs_path,
        meta_path=args.meta_path,
        yaml_path=args.yaml_path,
        output_path=args.output_path,
        doc_type_code=args.doc_type_code,
        output_format=args.output_format,
        debug=args.debug
    )
