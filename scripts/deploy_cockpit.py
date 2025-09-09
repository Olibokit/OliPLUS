# -*- coding: utf-8 -*-
"""
🚀 Script cockpitifié de déploiement Oliplus

Ce module exécute une série de scripts Python typés, affiche une barre de progression,
journalise les résultats et peut retourner un résumé JSON. Idéal pour les workflows CI/CD
ou les déploiements manuels en environnement distant.
"""

import subprocess
from pathlib import Path
import sys
import json
import argparse
import logging
from tqdm import tqdm
from datetime import datetime

# === Configuration cockpitifiée ===
LOG_FILE = "deploy_cockpit.log"
AVAILABLE_SCRIPTS = [
    "deploy_fragments_list.py",
    "deploy_classification_fragments.py",
    "deploy_dashboard_artifacts.py",
    "deploy_classification_files.py"
]

# === Initialisation du journal cockpitifié ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s",
    encoding="utf-8"
)

def run_scripts(scripts_to_run: list[str]) -> dict:
    """
    🧠 Exécute les scripts cockpitifiés et retourne un résumé typé.
    """
    result_summary = {"success": [], "failures": []}

    for script in tqdm(scripts_to_run, desc="🚀 Déploiement en cours", unit="script"):
        path = Path(script)

        if not path.exists():
            print(f"❌ Introuvable : {script}")
            result_summary["failures"].append(script)
            logging.warning(f"{script} introuvable")
            continue

        try:
            result = subprocess.run(
                [sys.executable, str(path)],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                print(f"✅ Succès : {script}")
                result_summary["success"].append(script)
                logging.info(f"{script} terminé avec succès")
            else:
                print(f"⚠️ Échec : {script} (code {result.returncode})")
                print(result.stderr.strip())
                result_summary["failures"].append(script)
                logging.error(f"{script} échoué – {result.stderr.strip()}")

        except Exception as e:
            print(f"🔥 Exception pour : {script} → {e}")
            result_summary["failures"].append(script)
            logging.exception(f"{script} exception levée")

    return result_summary

def main():
    """
    🎛️ Point d’entrée cockpitifié du script de déploiement.
    """
    parser = argparse.ArgumentParser(description="Déploiement cockpit Oliplus")
    parser.add_argument(
        "--scripts",
        nargs="+",
        default=AVAILABLE_SCRIPTS,
        help="Liste personnalisée des scripts à exécuter"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Affiche le retour JSON des statuts"
    )
    args = parser.parse_args()

    print("\n🚀 Lancement du déploiement cockpitifié...\n")
    summary = run_scripts(args.scripts)

    print("\n🧾 Résumé final du déploiement")
    print(f"✔️ Scripts réussis : {len(summary['success'])}/{len(args.scripts)}")
    if summary["failures"]:
        print("❌ Scripts échoués :")
        for s in summary["failures"]:
            print(f"   - {s}")
    else:
        print("🎉 Tous les déploiements ont réussi")

    if args.json:
        print("\n📦 Résultat JSON :")
        print(json.dumps(summary, indent=2, ensure_ascii=False))

    sys.exit(1 if summary["failures"] else 0)

if __name__ == "__main__":
    main()
