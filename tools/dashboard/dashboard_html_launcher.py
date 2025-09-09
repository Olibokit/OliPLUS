#!/usr/bin/env python
# 📘 dashboard_html_launcher.py — Générateur cockpit HTML dashboard OliPLUS

import os
import sys
import typer
import subprocess
import webbrowser
from pathlib import Path
from typing import List, Tuple

app = typer.Typer(help="🧱 Génération cockpit du tableau de bord HTML OliPLUS")

# === Chemins cockpit ===
PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
TOOLCHAIN_DIR: Path = PROJECT_ROOT / "OliPLUS.oliplus_toolchain" / "toolchain"
DEFAULT_DASHBOARD = PROJECT_ROOT / "dashboard" / "oliplus-dashboard-dynamic.html"
DASHBOARD_PATH: Path = Path(os.getenv("DASHBOARD_PATH", str(DEFAULT_DASHBOARD)))

# === Étapes cockpit ===
STEP_SCRIPTS: List[Tuple[str, Path]] = [
    ("📄 Scan des documents YAML/PDF", TOOLCHAIN_DIR / "structure_to_json.py"),
    ("📦 Génération payload JavaScript cockpit", TOOLCHAIN_DIR / "export_payload_for_html.py"),
    ("🗺️ Index YAML cockpit injecté", TOOLCHAIN_DIR / "generate_yaml_index.py")
]

def run_step(label: str, path: Path) -> bool:
    print(f"\n📡 {label}")
    if not path.exists():
        print(f"❌ Script introuvable : {path}")
        return False
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        print("⚠️ Erreur d'exécution :", e.stderr.strip())
        return False

@app.command("generate")
def generate_dashboard(
    open_browser: bool = typer.Option(True, "--open/--no-open", help="🌐 Ouvrir automatiquement le dashboard HTML"),
    verbose: bool = typer.Option(False, "--verbose", help="🔍 Afficher les détails d'exécution")
):
    """
    🧭 Lance la génération cockpit du tableau HTML OliPLUS.
    """
    print("\n🚀 Lancement cockpit — génération du tableau HTML")

    for label, script in STEP_SCRIPTS:
        success = run_step(label, script)
        if not success:
            print("⛔ Arrêt du cockpit — étape échouée.")
            raise typer.Exit(code=1)

    if DASHBOARD_PATH.exists():
        print(f"\n📁 Dashboard généré : {DASHBOARD_PATH.resolve()}")
        if open_browser:
            print("🌐 Ouverture du cockpit HTML...")
            webbrowser.open(DASHBOARD_PATH.resolve().as_uri())
            print("✅ Tableau de bord cockpit ouvert.")
    else:
        print(f"❌ HTML cockpit introuvable : {DASHBOARD_PATH}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
