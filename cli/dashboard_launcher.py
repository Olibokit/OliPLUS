import os
import subprocess
import webbrowser
import json
from pathlib import Path
from typing import Optional, List, Dict

import typer
from OliPLUS.OliPLUS.oliplus_toolchain.utils.validate_payload import validate_payload

app = typer.Typer(help="🚀 Démarrage cockpit OliPLUS via payload JSON")

# 📁 Chemins de base
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PAYLOAD_DIR = PROJECT_ROOT / "payloads"
COCKPIT_HTML = PROJECT_ROOT / "oliplus-dashboard-dynamic.html"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 🎨 Fonctions de log
log_entries: List[Dict[str, str]] = []

def log(msg: str, level: str = "INFO"):
    log_entries.append({"level": level, "message": msg})
    color = {
        "INFO": typer.colors.CYAN,
        "OK": typer.colors.GREEN,
        "WARN": typer.colors.YELLOW,
        "ERROR": typer.colors.RED
    }.get(level, typer.colors.WHITE)
    typer.secho(msg, fg=color)

def export_logs(filename: str = "cockpit.log", as_json: bool = False):
    path = LOG_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        if as_json:
            json.dump(log_entries, f, indent=2, ensure_ascii=False)
        else:
            for entry in log_entries:
                f.write(f"[{entry['level']}] {entry['message']}\n")
    log(f"📤 Logs exportés vers {path.name}", "OK")

# 🔍 Affiche les variables d’environnement utiles
def show_debug_env():
    log("🔍 Variables d’environnement :", "INFO")
    for var in ["API_KEY", "BASE_URL", "ENV", "DEBUG"]:
        value = os.getenv(var, "<non défini>")
        log(f"   - {var} = {value}", "WARN" if value == "<non défini>" else "OK")

# 📦 Sélection du payload
def select_payload(payload_override: Optional[Path]) -> Path:
    if payload_override and payload_override.exists():
        log(f"📦 Payload spécifié : {payload_override.name}", "OK")
        return payload_override

    json_files = sorted(PAYLOAD_DIR.glob("oliplus_payload_*.json"), key=os.path.getmtime, reverse=True)
    if not json_files:
        log("❌ Aucun fichier payload trouvé.", "ERROR")
        raise typer.Exit(1)

    log(f"📦 Dernier payload détecté : {json_files[0].name}", "OK")
    return json_files[0]

# 🧪 Validation du payload
def validate_payload_file(payload_path: Path) -> None:
    log("🧪 Validation de la structure du payload...", "INFO")
    is_valid, errors = validate_payload(str(payload_path))
    if not is_valid:
        log("⚠️ Payload invalide :", "ERROR")
        for err in errors:
            log(f"   - {err}", "ERROR")
        raise typer.Exit(1)
    log("✅ Payload valide, injection cockpit autorisée.", "OK")

# 🚀 Commande principale
@app.command()
def start(
    no_browser: bool = typer.Option(False, "--no-browser", help="Ne pas ouvrir le navigateur automatiquement"),
    skip_migrate: bool = typer.Option(False, "--skip-migrate", help="Ne pas relancer migrate.py"),
    payload_override: Optional[Path] = typer.Option(None, "--payload", "-p", help="Chemin d’un fichier payload à utiliser"),
    debug: bool = typer.Option(False, "--debug", help="Afficher les variables d’environnement"),
    export_log: Optional[str] = typer.Option(None, "--export-log", help="Nom du fichier log à exporter"),
    json_log: bool = typer.Option(False, "--json-log", help="Exporter les logs au format JSON")
) -> None:
    """Lance cockpit OliPLUS depuis le dernier payload JSON (ou chemin fourni)."""

    if debug:
        show_debug_env()

    if not skip_migrate:
        log("🚀 Génération du payload cockpit...", "INFO")
        try:
            subprocess.run(["python", "migrate.py"], check=True, cwd=PROJECT_ROOT)
        except subprocess.CalledProcessError as e:
            log(f"❌ Échec migrate.py : {e}", "ERROR")
            raise typer.Exit(1)

    payload_file = select_payload(payload_override)
    validate_payload_file(payload_file)

    if not COCKPIT_HTML.exists():
        log(f"❌ Fichier HTML introuvable : {COCKPIT_HTML}", "ERROR")
        raise typer.Exit(1)

    if no_browser:
        typer.echo(f"📎 Cockpit prêt : {COCKPIT_HTML}")
    else:
        log("🧠 Ouverture du cockpit dans ton navigateur...", "INFO")
        webbrowser.open(COCKPIT_HTML.as_uri())

    if export_log:
        export_logs(export_log, as_json=json_log)

if __name__ == "__main__":
    app()
