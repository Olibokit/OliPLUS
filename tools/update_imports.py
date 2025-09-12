import os
import re
from pathlib import Path
from datetime import datetime

# 📦 Nom du package racine
ROOT_PACKAGE = "OliPLUS"

# 🧹 Dossiers à ignorer
IGNORED_DIRS = {"__pycache__", ".venv", "venv", ".git", ".mypy_cache", "dist", "build"}

# 🔁 Règles de remplacement des imports
IMPORT_PATTERNS = {
    r'from\s+OliPLUS.oliplus_models\s+import': f'from {ROOT_PACKAGE}.OliPLUS.oliplus_models import',
    r'from\s+OliPLUS.oli_db_models\s+import': f'from {ROOT_PACKAGE}.OliPLUS.oli_db_models import',
    r'from\s+OliPLUS.oliplus_toolchain\.': f'from {ROOT_PACKAGE}.OliPLUS.oliplus_toolchain.',
}

def update_imports(file_path: Path, dry_run=False) -> bool:
    content = file_path.read_text(encoding="utf-8")
    updated = content

    for pattern, replacement in IMPORT_PATTERNS.items():
        updated = re.sub(pattern, replacement, updated)

    if updated != content:
        if dry_run:
            print(f"🔍 Simulation : {file_path} serait modifié.")
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = file_path.with_suffix(file_path.suffix + f".bak.{timestamp}")
            file_path.rename(backup_path)
            file_path.write_text(updated, encoding="utf-8")
            print(f"✔ Imports mis à jour dans : {file_path} (backup : {backup_path.name})")
        return True
    return False

def walk_python_files(base_path=".", dry_run=False) -> int:
    root = Path(base_path).resolve()
    count = 0

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for fname in filenames:
            if fname.endswith(".py") and not fname.startswith("__"):
                fpath = Path(dirpath) / fname
                if update_imports(fpath, dry_run=dry_run):
                    count += 1
    return count

if __name__ == "__main__":
    dry_run = "--dry-run" in os.sys.argv
    total = walk_python_files(".", dry_run=dry_run)

    if dry_run:
        print(f"\n🧪 Simulation terminée : {total} fichier(s) seraient modifiés.")
    elif total:
        print(f"\n📦 {total} fichier(s) modifié(s).")
    else:
        print("✅ Aucun import à mettre à jour.")
