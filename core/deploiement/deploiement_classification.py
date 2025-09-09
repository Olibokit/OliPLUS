from pathlib import Path
import shutil
import datetime
import sys
import traceback

# === CONFIGURATION COCKPIT ===
racine_source = Path(__file__).resolve().parent
destination_root = (
    racine_source.parent
    / "OliPLUS"
    / "6000_INFORMATION_ET_COMMUNICATIONS"
    / "1100_GOUVERNANCE_INFORMATION"
)

destination_root.mkdir(parents=True, exist_ok=True)

fichiers_cible = [
    "classification_plan.yaml",
    "classification_export.json",
    "classification_export.csv",
    "classification_export.md",
]

logfile = destination_root / ".copilot_classification.log"
log_lines = []

# === UTILITAIRE DE LOG COCKPIT ===
def log(msg, level="INFO"):
    now = datetime.datetime.now().isoformat(timespec="seconds")
    prefix = {
        "INFO": "ℹ️",
        "SUCCESS": "✅",
        "ERROR": "🚨",
        "WARNING": "⚠️",
        "MISSING": "❌"
    }.get(level, "🔍")
    line = f"[{now}] {prefix} {msg}"
    log_lines.append(line)
    print(line, file=sys.stderr if level in ["ERROR", "WARNING"] else sys.stdout)

# === DÉPLOIEMENT COCKPITIFIÉ ===
def deploiement_classification():
    log("Déploiement cockpit vers dossier documentaire final", level="INFO")

    for fname in fichiers_cible:
        src = racine_source / fname
        dst = destination_root / fname

        if src.exists():
            try:
                shutil.move(str(src), str(dst))
                log(f"Déplacé : {fname}", level="SUCCESS")
            except Exception as e:
                log(f"Erreur de déplacement {fname} — {e}", level="ERROR")
                log(traceback.format_exc(), level="ERROR")
        else:
            log(f"Introuvable : {fname}", level="MISSING")

# === ÉCRITURE DU JOURNAL COCKPITIFIÉ ===
def ecrire_journal():
    try:
        logfile.parent.mkdir(parents=True, exist_ok=True)
        with logfile.open("a", encoding="utf-8") as f:
            f.write("\n".join(log_lines) + "\n")
        log(f"Journal cockpit mis à jour : {logfile.name}", level="SUCCESS")
    except Exception as e:
        log(f"Erreur d’écriture dans le journal cockpit — {e}", level="ERROR")
        log(traceback.format_exc(), level="ERROR")

# === POINT D'ENTRÉE COCKPITIFIÉ ===
if __name__ == "__main__":
    deploiement_classification()
    ecrire_journal()
