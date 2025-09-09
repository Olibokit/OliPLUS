import os
import shutil
import yaml
import logging
import argparse
import datetime
import platform
import subprocess
from pathlib import Path
from collections import Counter
import sys

# 🔧 Configuration
ROOT = Path.cwd()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("yaml_executor")

# 🖥️ Interface CLI
def parse_args():
    parser = argparse.ArgumentParser(description="🧠 Exécuteur de plan YAML cockpit")
    parser.add_argument("--plan", type=str, required=True, help="Chemin vers le fichier YAML")
    parser.add_argument("--dry-run", action="store_true", help="Simuler sans déplacer")
    parser.add_argument("--rapport", type=str, help="Chemin personnalisé pour le rapport Markdown")
    parser.add_argument("--source", type=str, default="à_trier", help="Dossier contenant les fichiers à analyser")
    return parser.parse_args()

# 📦 Création du dossier cible
def ensure_directory(path: Path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        init_file = path / "__init__.py"
        init_file.touch()
        logger.info(f"📁 Dossier créé : {path}")

# 🚚 Déplacement du fichier
def move_file(filepath: Path, target: Path, dry_run=False, log_entries=None):
    if not filepath.exists():
        msg = f"⚠️ Fichier introuvable : {filepath.name}"
        logger.warning(msg)
        if log_entries is not None:
            log_entries.append(msg)
        return
    ensure_directory(target)
    destination = target / filepath.name
    if destination.exists():
        msg = f"⚠️ Doublon détecté : {filepath.name} déjà présent dans {target}"
        logger.warning(msg)
        if log_entries is not None:
            log_entries.append(msg)
        return
    if dry_run:
        msg = f"🧪 Simulation : {filepath.name} → {target}"
        logger.info(msg)
    else:
        shutil.move(str(filepath), str(destination))
        msg = f"✅ Déplacé : {filepath.name} → {target}"
        logger.info(msg)
    if log_entries is not None:
        log_entries.append(msg)

# 📜 Lecture et exécution du plan YAML
def execute_yaml_plan(plan_path: Path, source_dir: Path, dry_run=False):
    log_entries = []
    try:
        with open(plan_path, "r", encoding="utf-8") as f:
            plan = yaml.safe_load(f)
    except Exception as e:
        msg = f"❌ Erreur lecture YAML : {e}"
        logger.error(msg)
        log_entries.append(msg)
        return log_entries

    for section in ["prioritaires", "archiver_documenter", "obsoletes", "migration_oliplus"]:
        entries = plan.get(section, [])
        for item in entries:
            filename = item.get("fichier")
            action = item.get("action", "")
            motif = item.get("motif", "")
            target_folder = item.get("target")
            filepath = source_dir / filename

            if action == "move":
                if not target_folder:
                    msg = f"⚠️ Aucun dossier cible défini pour {filename}"
                    logger.warning(msg)
                    log_entries.append(msg)
                    continue
                target_path = ROOT / target_folder
                move_file(filepath, target_path, dry_run, log_entries)
            elif action == "delete":
                if dry_run:
                    msg = f"🧪 Simulation suppression : {filename} — {motif}"
                    logger.info(msg)
                    log_entries.append(msg)
                else:
                    if filepath.exists():
                        filepath.unlink()
                        msg = f"🗑️ Supprimé : {filename} — {motif}"
                        logger.info(msg)
                        log_entries.append(msg)
                    else:
                        msg = f"⚠️ Fichier à supprimer introuvable : {filename}"
                        logger.warning(msg)
                        log_entries.append(msg)
            else:
                msg = f"❓ Action inconnue pour {filename} : {action}"
                logger.warning(msg)
                log_entries.append(msg)

    return log_entries

# 📝 Sauvegarde du rapport Markdown
def save_markdown_report(log_entries, dry_run=False, output_path=None):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    default_name = f"rapport_migration_{'simulation' if dry_run else 'reelle'}_{timestamp}.md"
    path = Path(output_path) if output_path else ROOT / default_name

    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)

    stats = Counter()
    for entry in log_entries:
        if "✅ Déplacé" in entry:
            stats["déplacés"] += 1
        elif "🗑️ Supprimé" in entry:
            stats["supprimés"] += 1
        elif "🧪 Simulation" in entry:
            stats["simulés"] += 1
        elif "⚠️" in entry:
            stats["avertissements"] += 1

    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Rapport de migration cockpit\n")
        f.write(f"📅 Date : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"🧪 Mode : {'Simulation' if dry_run else 'Réel'}\n\n")

        f.write("## 📊 Statistiques\n")
        for key, value in stats.items():
            f.write(f"- {key.capitalize()} : {value}\n")
        f.write("\n---\n\n")

        f.write("## 📋 Détails des opérations\n")
        for entry in log_entries:
            f.write(f"- {entry}\n")

    logger.info(f"📄 Rapport sauvegardé : {path.resolve()}")
    return path

# 🖥️ Ouvre le rapport automatiquement
def open_report(path: Path):
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.run(["open", str(path)])
        elif platform.system() == "Linux":
            subprocess.run(["xdg-open", str(path)])
    except Exception as e:
        logger.warning(f"⚠️ Impossible d’ouvrir le rapport automatiquement : {e}")

# 🚀 Point d’entrée
if __name__ == "__main__":
    args = parse_args()
    SOURCE_DIR = ROOT / args.source

    if not SOURCE_DIR.exists():
        logger.error(f"❌ Dossier source introuvable : {SOURCE_DIR}")
        sys.exit(1)

    plan_file = Path(args.plan)
    if plan_file.exists():
        logs = execute_yaml_plan(plan_file, SOURCE_DIR, dry_run=args.dry_run)
        rapport_path = save_markdown_report(logs, dry_run=args.dry_run, output_path=args.rapport)
        open_report(rapport_path)
    else:
        logger.error(f"❌ Fichier YAML introuvable : {args.plan}")
