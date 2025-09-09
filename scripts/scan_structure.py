from pathlib import Path
import json
from datetime import datetime

# === CONFIGURATION ===
ROOT_DIR = Path("A travailler")
OUTPUT_PATH = Path("oliplus_data/structure_output.json")
EXCLUDE_FOLDERS = {"archives", "_tmp", ".git", "__pycache__"}

EXTENSION_TYPE_MAP = {
    ".pdf": "PDF", ".docx": "DOCX", ".txt": "Text", ".py": "Python", ".ipynb": "Notebook",
    ".md": "Markdown", ".cpp": "C++", ".h": "Header C", ".json": "JSON", ".yaml": "YAML",
    ".jpg": "Image", ".jpeg": "Image", ".png": "Image", ".gif": "Image",
    ".zip": "Archive", ".tar": "Archive", ".rar": "Archive"
}

def determine_type(file: Path) -> str:
    return EXTENSION_TYPE_MAP.get(file.suffix.lower(), "Autre")

def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_FOLDERS for part in path.parts)

# === SCAN DES FICHIERS ===
structure = []
files_found = 0
anomalies = 0
obsoletes = 0

for file in ROOT_DIR.rglob("*.*"):
    if not file.is_file() or is_excluded(file):
        continue

    try:
        relative_path = file.relative_to(ROOT_DIR)
        size_bytes = file.stat().st_size
        last_modified = datetime.fromtimestamp(file.stat().st_mtime).isoformat()
    except Exception as e:
        print(f"⛔️ Erreur avec {file}: {e}")
        continue

    extension = file.suffix.lower()
    status = "à revoir"
    anomaly = False
    recommandation = "Analyser pour cockpit"

    if size_bytes < 500:
        anomaly = True
        status = "suspect"
        recommandation = "Vérifier contenu ou supprimer"
        anomalies += 1
    elif extension in [".old", ".bak", ".tmp", ".~", ".log"]:
        status = "obsolète"
        recommandation = "Archiver ou nettoyer"
        obsoletes += 1

    file_info = {
        "title": file.stem.strip(),
        "extension": extension,
        "type": determine_type(file),
        "folder": str(relative_path.parent),
        "size_bytes": size_bytes,
        "size_kb": round(size_bytes / 1024, 2),
        "last_modified": last_modified,
        "status": status,
        "anomaly": anomaly,
        "is_similar_to_existing": False,
        "cockpit_path": f"OIIPLUS/{relative_path}",
        "recommandation": recommandation
    }

    structure.append(file_info)
    files_found += 1

# === SAUVEGARDE JSON ===
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump({
        "résumé": {
            "fichiers_total": files_found,
            "anomalies_detectées": anomalies,
            "fichiers_obsolètes": obsoletes,
            "cockpit_ready": files_found - anomalies - obsoletes,
            "scan_date": datetime.now().isoformat()
        },
        "structure": structure
    }, f, indent=2, ensure_ascii=False)

print(f"✅ Scan terminé : {files_found} fichiers détectés.")
print(f"🚨 Anomalies : {anomalies}, Obsolètes : {obsoletes}")
print(f"📁 Fichier généré : {OUTPUT_PATH}")
