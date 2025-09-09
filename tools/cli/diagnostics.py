import typer
from pathlib import Path
from datetime import datetime
import importlib
import sys

app = typer.Typer(help="🩺 Outils de diagnostic pour le cockpit OliPLUS")

# 📁 Racine du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# 📂 Scripts essentiels
SCRIPTS = [
    "generate_cockpit_files_section.py",
    "migrate.py",
    "refresh_payload_and_open_html.py"
]

# 🔌 Modules CLI attendus
CLI_MODULES = [
    "catalog_fragment",
    "payload",
    "diagnostics"
]

@app.command("doctor")
def doctor(export: bool = typer.Option(False, "--export", help="📤 Exporter le rapport de diagnostic")):
    typer.echo("🧪 Diagnostic du cockpit OliPLUS\n")
    lines = []
    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 🧾 En-tête
    lines.append("# 🧪 Rapport de diagnostic cockpit")
    lines.append(f"📅 Généré le : {today}")
    lines.append(f"🖥️ Version Python : {sys.version.split()[0]}")
    lines.append("\n---\n")

    # 📂 Vérification des scripts
    typer.echo("📂 Vérification des scripts essentiels :")
    lines.append("## 📂 Scripts essentiels\n")
    for script in SCRIPTS:
        path = PROJECT_ROOT / script
        if path.exists():
            typer.secho(f"   ✅ {script}", fg=typer.colors.GREEN)
            lines.append(f"- ✅ `{script}`")
        else:
            typer.secho(f"   ❌ {script} manquant", fg=typer.colors.RED)
            lines.append(f"- ❌ `{script}` ❗ (attendu dans `{path.relative_to(PROJECT_ROOT)}`)")

    # 🔌 Vérification des modules CLI
    typer.echo("\n🔌 Vérification des modules CLI :")
    lines.append("\n## 🔌 Modules CLI\n")
    for mod in CLI_MODULES:
        try:
            imported = importlib.import_module(f"OliPLUS.oliplus_toolchain.cli_commands.{mod}")
            app_obj = getattr(imported, "app", None) or getattr(imported, f"{mod}_app", None)
            if app_obj:
                typer.secho(f"   ✅ {mod}", fg=typer.colors.GREEN)
                lines.append(f"- ✅ `{mod}` (Typer app détecté)")
            else:
                typer.secho(f"   ⚠️  {mod} importé mais sans Typer app", fg=typer.colors.YELLOW)
                lines.append(f"- ⚠️ `{mod}` présent mais sans `app`")
        except ImportError as e:
            typer.secho(f"   ❌ {mod} introuvable", fg=typer.colors.RED)
            lines.append(f"- ❌ `{mod}` introuvable ({e})")

    # ✅ Résumé
    lines.append("\n---\n")
    lines.append("✅ Diagnostic terminé avec succès.")

    typer.echo("\n📊 Diagnostic terminé.")

    # 💾 Export du rapport
    if export:
        report_path = PROJECT_ROOT / "diagnostic_rapport.md"
        report_path.write_text("\n".join(lines), encoding="utf-8")
        typer.echo(f"\n💾 Rapport exporté : `{report_path.relative_to(PROJECT_ROOT)}`")

if __name__ == "__main__":
    app()
