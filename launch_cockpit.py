"""
🚀 Module de lancement cockpitifié — OliPLUS
Initialise les composants critiques, vérifie les dépendances, et propulse le cockpit.
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime

# 📁 Définition des chemins cockpit
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "manifest" / "cockpit_manifest_master.yaml"
LOG_PATH = BASE_DIR / "logs" / "launch.log"

# 📝 Initialisation du journal cockpit
logging.basicConfig(filename=LOG_PATH, level=logging.INFO)
logging.info(f"[{datetime.now().isoformat()}] 🚀 Lancement cockpit initialisé")

# 🔍 Vérification des modules essentiels
REQUIRED_MODULES = [
    "dashboard_ui.py",
    "SyncEngine.py",
    "cockpit_manifest_master.yaml"
]

def check_modules():
    missing = []
    for module in REQUIRED_MODULES:
        path = BASE_DIR / module
        if not path.exists():
            missing.append(module)
            logging.warning(f"❌ Module manquant : {module}")
        else:
            logging.info(f"✅ Module détecté : {module}")
    return missing

# 🧠 Lancement cockpit
def launch_cockpit():
    print("🧭 Lancement cockpitifié en cours...")
    missing = check_modules()
    if missing:
        print("❌ Modules manquants :")
        for m in missing:
            print(f"   - {m}")
        sys.exit("⛔ Lancement interrompu — modules critiques absents.")
    print("✅ Tous les modules critiques sont présents.")
    print("📦 Initialisation cockpit terminée.")

if __name__ == "__main__":
    launch_cockpit()
