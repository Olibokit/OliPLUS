# 📘 dashboard_ui.py — Orchestrateur HTML cockpit OliPLUS

import subprocess
import webbrowser
from pathlib import Path
import sys
import logging

# 🔧 Configuration du logging cockpit
logging.basicConfig(level=logging.INFO, format="%(message)s")

# 📁 Chemins cockpitifiés
COCKPIT_HTML_PATH = Path("dashboard/oliplus-dashboard-dynamic.html")
TOOLCHAIN_DIR = Path("OliPLUS.oliplus_toolchain/toolchain")

# ✅ Étapes cockpit typées
STEPS = [
    {
        "id": "1",
        "label": "📄 Étape 1/3 — Scan des documents YAML/PDF",
        "script": TOOLCHAIN_DIR / "structure_to_json.py"
    },
    {
        "id": "2",
        "label": "📦 Étape 2/3 — Génération payload JavaScript cockpit",
        "script": TOOLCHAIN_DIR / "export_payload_for_html.py"
    },
    {
        "id": "3",
        "label": "🗺️ Étape 3/3 — Index YAML cockpit injecté",
        "script": TOOLCHAIN_DIR / "generate_yaml_index.py"
    }
]

def run_step(label: str, script_path: Path) -> bool:
    logging.info(f"\n📡 {label}")
    if not script_path.exists():
        logging.error(f"❌ Script introuvable : {script_path}")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True, text=True, check=True
        )
        if result.stdout:
            logging.info(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"⚠️ Erreur d’exécution : {e.stderr.strip()}")
        logging.error(f"🔍 Code retour : {e.returncode}")
        logging.error(f"📄 Script : {script_path}")
        return False

def open_dashboard(html_path: Path):
    if html_path.exists() and html_path.stat().st_size > 0:
        logging.info(f"\n🌐 Ouverture du cockpit HTML : {html_path}")
        webbrowser.open(html_path.resolve().as_uri())
        logging.info("✅ Tableau de bord cockpit ouvert.")
    else:
        logging.error(f"❌ Fichier HTML introuvable ou vide : {html_path}")

def main():
    logging.info("\n🧭 Lancement cockpit OliPLUS — Orchestration typée YAML / HTML")

    dry_run = "--dry-run" in sys.argv
    step_arg = next((arg for arg in sys.argv if arg.startswith("--step=")), None)
    selected_step = step_arg.split("=")[1] if step_arg else None

    if dry_run:
        logging.info("🧪 Mode dry-run activé — aucune exécution réelle.")
        for step in STEPS:
            logging.info(f"🔍 Étape simulée : {step['label']} → {step['script']}")
        sys.exit(0)

    results = []

    for step in STEPS:
        if selected_step and step["id"] != selected_step:
            continue
        success = run_step(step["label"], step["script"])
        results.append((step["label"], success))
        if not success:
            logging.error("⛔ Arrêt du cockpit — étape échouée.")
            sys.exit(1)

    if not selected_step:
        open_dashboard(COCKPIT_HTML_PATH)

    # 📊 Résumé final cockpit
    logging.info("\n📊 Résumé cockpit :")
    for label, success in results:
        status = "✅" if success else "❌"
        logging.info(f"{status} {label}")

if __name__ == "__main__":
    main()
