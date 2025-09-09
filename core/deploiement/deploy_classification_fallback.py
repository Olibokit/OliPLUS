from pathlib import Path
import shutil
import datetime
import sys
import traceback

# === CONFIGURATION COCKPIT ===
SOURCE_DIR = Path(__file__).resolve().parent
DESTINATION_DIR = (
    SOURCE_DIR.parent / "OliPLUS" /
    "6000_INFORMATION_ET_COMMUNICATIONS" /
    "1100_GOUVERNANCE_INFORMATION"
)
DESTINATION_DIR.mkdir(parents=True, exist_ok=True)

FICHIERS_CIBLE = [
    "classification_plan.yaml",
    "classification_export.json",
    "classification_export.csv",
    "classification_export.md"
]

LOG_FILE = DESTINATION_DIR / ".copilot_classification.log"
LOG_LINES = []

# === UTILITAIRE DE LOG COCKPIT
def log(msg, level="INFO"):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"[{now}][{level}] {msg}"
    LOG_LINES.append(line)
    print(line)

# === DÉPLOIEMENT COCKPIT
log("🧠 Déploiement cockpit des fichiers de classification")

for fname in FICHIERS_CIBLE:
    src = SOURCE_DIR / fname
    dst = DESTINATION_DIR / fname

    if src.exists():
        try:
            shutil.move(str(src), str(dst))
            log(f"✅ Déplacé : {fname}")
        except Exception as e:
            log(f"⚠️ Erreur déplacement {fname} → {e}", level="ERROR")
            try:
                shutil.copy2(str(src), str(dst))
                log(f"📋 Copié en fallback : {fname}")
            except Exception as fallback_error:
                log(f"❌ Échec total pour {fname} → {fallback_error}", level="CRITICAL")
                traceback.print_exc(file=sys.stderr)
    else:
        log(f"❌ Introuvable : {fname}", level="WARNING")

# === ÉCRITURE DU JOURNAL COCKPIT
try:
    with open(LOG_FILE, "a", encoding="utf-8") as log_f:
        log_f.write("\n".join(LOG_LINES) + "\n")
    log(f"🧾 Journal mis à jour : {LOG_FILE.name}")
except Exception as e:
    log(f"🚨 Impossible d’écrire dans le log : {e}", level="ERROR")
    traceback.print_exc(file=sys.stderr)

# === RÉCAPITULATIF FINAL
log("📦 Déploiement terminé.", level="INFO")
