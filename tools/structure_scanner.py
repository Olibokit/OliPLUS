from pathlib import Path
import json
import logging
from datetime import datetime

# 🧩 Configuration cockpit
ROOT_DIR = Path("A travailler")
OUTPUT_PATH = Path("oliplus_data/structure_output.json")
EXCLUDE_FOLDERS = {"archives", "_tmp", ".git", "__pycache__"}
EXTENSION_TYPE_MAP = {
    ".pdf": "PDF", ".docx": "DOCX", ".txt": "Texte", ".py": "Python",
    ".md": "Markdown", ".cpp": "C++", ".h": "Header C", ".json": "JSON",
    ".yaml": "YAML", ".yml": "YAML", ".jpg": "Image", ".png": "Image",
    ".zip": "Archive", ".csv": "CSV", ".xlsx": "Excel", ".log": "Log"
}
SUSPECT_EXTENSIONS = {".old", ".bak", ".tmp", ".~", ".log"}

# 🪵 Logger cockpit
logger = logging.getLogger("structure_scanner")
logging.basicConfig(level=logging.INFO, format="📘 %(message)s")

def determine_type(file: Path) -> str:
    return EXTENSION_TYPE_MAP.get(file.suffix.lower(), "Autre")

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_FOLDERS for part in path.parts)

def detect_flags(file_info: dict) -> list:
    flags = []
    if file_info["size_bytes"] < 500:
        flags.append("taille faible")
    if file_info["extension"] in SUSPECT_EXTENSIONS:
        flags.append("extension suspecte")
    if "~" in file_info["title"] or file_info["title"].startswith("._"):
        flags.append("nom suspect")
    return flags

def scan_structure(root_dir: Path) -> dict:
    structure = []
    stats = {"total": 0, "suspects": 0, "obsoletes": 0, "anomalies": 0}

    for file in root_dir.rglob("*.*"):
        if not file.is_file() or is_excluded(file):
            continue

        relative_path = file.relative_to(root_dir)
        file_info = {
            "title": file.stem,
            "extension": file.suffix.lower(),
            "type": determine_type(file),
            "folder": str(relative_path.parent),
            "size_bytes": file.stat().st_size,
            "last_modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
            "status": "à revoir",
            "flags": []
        }

        flags = detect_flags(file_info)
        file_info["flags"] = flags

        if "taille faible" in flags:
            file_info["status"] = "suspect"
            stats["suspects"] += 1
        elif "extension suspecte" in flags:
            file_info["status"] = "obsolète"
            stats["obsoletes"] += 1

        if flags:
            stats["anomalies"] += 1

        structure.append(file_info)
        stats["total"] += 1

    logger.info(f"✅ Scan terminé : {stats['total']} fichiers analysés.")
    logger.info(f"🔍 Anomalies détectées : {stats['anomalies']} (suspects: {stats['suspects']}, obsolètes: {stats['obsoletes']})")

    return {
        "generated_at": datetime.now().isoformat(),
        "root": str(root_dir),
        "stats": stats,
        "files": structure
    }

def export_json(data: dict, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"📁 Fichier cockpit généré : {output_path}")

if __name__ == "__main__":
    structure_data = scan_structure(ROOT_DIR)
    export_json(structure_data, OUTPUT_PATH)
