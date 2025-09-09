#!/usr/bin/env python3

import datetime
import logging
from pathlib import Path
import re
from typing import List, Optional

import typer

app = typer.Typer()
logging.basicConfig(level=logging.INFO, format="📘 %(message)s")
logger = logging.getLogger("changelog")

DEFAULT_CHANGELOG_FILE = Path("CHANGELOG.md")

def collect_lines(prompt: str) -> List[str]:
    logger.info(prompt)
    lines = []
    while True:
        line = input("- ").strip()
        if not line:
            break
        if line not in lines:
            lines.append(line)
    return lines

def validate_version(version: str) -> bool:
    return bool(re.match(r"^\d+\.\d+\.\d+$", version))

def prompt_metadata() -> tuple:
    while True:
        version = input("📝 Nouvelle version (ex: 0.2.1) : ").strip()
        if validate_version(version):
            break
        logger.warning("❌ Format invalide. Utilise x.y.z (ex: 1.0.3)")

    date = datetime.date.today().isoformat()
    logger.info(f"📅 Date : {date}")

    features = collect_lines("✨ Nouvelles fonctionnalités (ligne vide pour terminer) :")
    improvements = collect_lines("🔧 Améliorations techniques :")
    fixes = collect_lines("🐛 Correctifs :")

    return version, date, features, improvements, fixes

def format_changelog_entry(version: str, date: str, features: List[str], improvements: List[str], fixes: List[str]) -> str:
    lines = [f"## [{version}] – {date}"]
    if features:
        lines.append("### ✨ Nouvelles fonctionnalités")
        lines.extend([f"- {f}" for f in features])
    if improvements:
        lines.append("### 🔧 Améliorations techniques")
        lines.extend([f"- {f}" for f in improvements])
    if fixes:
        lines.append("### 🐛 Correctifs")
        lines.extend([f"- {f}" for f in fixes])
    return "\n".join(lines) + "\n\n"

def ensure_changelog_exists(file_path: Path):
    if not file_path.exists():
        logger.info(f"📄 Fichier {file_path.name} absent → création")
        file_path.write_text("# 📝 Journal des modifications cockpit\n\n", encoding="utf-8")

def insert_entry_at_top(file_path: Path, entry: str):
    content = file_path.read_text(encoding="utf-8")
    marker = "## ["
    idx = content.find(marker)
    updated = content + "\n" + entry if idx == -1 else content[:idx] + entry + content[idx:]
    file_path.write_text(updated, encoding="utf-8")

def extract_latest_entry(file_path: Path) -> Optional[str]:
    content = file_path.read_text(encoding="utf-8")
    entries = content.split("## [")
    if len(entries) < 2:
        return None
    latest = "## [" + entries[1]
    next_entry_idx = latest.find("## [", 5)
    return latest[:next_entry_idx] if next_entry_idx != -1 else latest

@app.command()
def add(
    dry_run: bool = typer.Option(False, help="Prévisualiser sans écrire dans le fichier"),
    file: Path = typer.Option(DEFAULT_CHANGELOG_FILE, help="Chemin vers le fichier changelog")
):
    """
    Ajouter une nouvelle entrée au changelog.
    """
    ensure_changelog_exists(file)
    version, date, features, improvements, fixes = prompt_metadata()
    entry = format_changelog_entry(version, date, features, improvements, fixes)

    logger.info("\n📋 Aperçu de l'entrée :\n")
    print(entry)

    if dry_run:
        logger.info("🧪 Mode simulation activé : aucune modification enregistrée")
    else:
        insert_entry_at_top(file, entry)
        logger.info(f"✅ Entrée changelog {version} ajoutée avec succès → {file.name}")

@app.command()
def show_latest(file: Path = typer.Option(DEFAULT_CHANGELOG_FILE, help="Chemin vers le fichier changelog")):
    """
    Affiche la dernière entrée du changelog.
    """
    if not file.exists():
        logger.warning(f"❌ Fichier {file.name} introuvable")
        raise typer.Exit()

    latest = extract_latest_entry(file)
    if latest:
        logger.info("\n📦 Dernière entrée du changelog :\n")
        print(latest)
    else:
        logger.info("ℹ️ Aucune entrée trouvée dans le changelog.")

if __name__ == "__main__":
    app()
