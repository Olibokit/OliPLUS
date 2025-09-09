# 🧠 oli_cli.py — Interface CLI cockpitifiée pour gouvernance typée Oliplus

import os, json
from typer import Typer, Context, Option
from rich import print
from rich.table import Table

# === 🔧 Chargement config cockpit
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "json", "config.json")
try:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    config = {}
    print(f"[red]❌ Erreur de chargement config.json : {e}[/red]")

# === 🧭 Initialisation CLI
app = Typer(help="📘 CLI souveraine Oliplus — gouvernance cockpitifiée")
debug = False

@app.callback()
def main(ctx: Context, debug_flag: bool = Option(False, "--debug", help="🔍 Mode debug cockpit")):
    global debug
    debug = debug_flag
    if debug:
        print("[bold yellow]🛠️ Mode debug activé[/bold yellow]")

# === 📊 Dashboards
from cli_commands.dashboard_launcher import launch as launch_streamlit_dashboard
from cli_commands.document_dashboard_viewer import main as launch_document_dashboard
from cli_commands.upload_documents_viewer import main as launch_upload_dashboard
from cli_commands.dashboard_html_launcher import (
    generate_dashboard as generate_html_dashboard,
    launch as launch_html_dashboard
)
from cli_commands.dashboard_payload_cli import generate as generate_html_payload
from cli_commands.dashboard_docker_launcher import launch as launch_docker_services_view

# === 📁 Documents & injections
from cli_commands.oli_injector import main as inject_document_blobs
from cli_commands.cli_teedy_injector import main as launch_teedy_cli
from cli_commands.cli_classification_viewer import main as launch_classification_viewer

# === 📈 Suivi & audit
from cli_commands.oli_show_progress import main as launch_progress_view
from cli_commands.oli_export_progress_yaml import main as export_progress_as_yaml
from cli_commands.extract_models_yaml import main as extract_django_models_yaml
from cli_commands.exceptions_viewer import main as show_exceptions_viewer

# === 🎨 Visualisation cockpit
from cockpit_tools.visual.render_blender import main as launch_blender_render
from cockpit_tools.visual.gltf_injector import main as convert_collada_gltf

# === 🔐 Certification
from cli_commands.cockpit_certifier import certify as certify_component

# === 🚀 Démarrage cockpit
from OliPLUS.core.boot.cockpit_boot import main as launch_cockpit_boot

# === 📦 Dépendances optionnelles
try:
    from cli_commands.dependencies_viewer import main as launch_dependencies_view
except ImportError:
    launch_dependencies_view = lambda: print("📦 Module 'dependencies_viewer' non disponible.")

# === 🧭 Commande interactive
@app.command("interactive")
def interactive_mode():
    print("\n🧭 Mode interactif cockpit — tapez une commande ou 'exit'")
    while True:
        cmd = input("🔹 > ").strip()
        if cmd in ["exit", "quit"]:
            print("👋 Fermeture cockpit CLI.")
            break
        try:
            app([cmd])
        except Exception as e:
            print(f"[red]❌ Erreur : {e}[/red]")

# === 🧭 Commande list
@app.command("list")
def list_commands():
    print("\n📘 Commandes cockpit disponibles :\n")
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Commande", style="green")
    table.add_column("Description")

    commands = {
        "boot": "Démarrage cockpit typé",
        "dashboard": "Dashboard Streamlit principal",
        "document-dashboard": "Interface documents & stats",
        "upload-dashboard": "Injection documentaire",
        "inject": "Injection YAML / EPUB / PDF",
        "inject-teedy": "Injecteur vers Teedy cockpit",
        "classify": "Viewer du plan de classement YAML",
        "progress": "État des blocs cockpit",
        "export-progress": "Export YAML de la progression",
        "models": "Extraction des modèles Django",
        "errors": "Typologie des exceptions cockpit",
        "dependencies": "Viewer des dépendances cockpit",
        "docker-dashboard": "Monitoring Docker cockpit",
        "html-dashboard": "Génération dashboard HTML",
        "launch": "Ouverture dashboard HTML",
        "payload": "Génération JS cockpit pour HTML",
        "render": "Blender render cockpit (.blend → .png)",
        "convert": "COLLADA → glTF cockpit",
        "certify": "Certification composant cockpit",
        "interactive": "Mode CLI interactif cockpit",
        "list": "Affiche cette vue CLI cockpit"
    }

    for cmd, desc in commands.items():
        table.add_row(cmd, desc)
    print(table)

# === 🧭 Mapping cockpit : commandes CLI
app.command("boot")(launch_cockpit_boot)
app.command("dashboard")(launch_streamlit_dashboard)
app.command("document-dashboard")(launch_document_dashboard)
app.command("upload-dashboard")(launch_upload_dashboard)
app.command("inject")(inject_document_blobs)
app.command("inject-teedy")(launch_teedy_cli)
app.command("classify")(launch_classification_viewer)
app.command("progress")(launch_progress_view)
app.command("export-progress")(export_progress_as_yaml)
app.command("models")(extract_django_models_yaml)
app.command("errors")(show_exceptions_viewer)
app.command("dependencies")(launch_dependencies_view)
app.command("docker-dashboard")(launch_docker_services_view)
app.command("html-dashboard")(generate_html_dashboard)
app.command("launch")(launch_html_dashboard)
app.command("payload")(generate_html_payload)
app.command("render")(launch_blender_render)
app.command("convert")(convert_collada_gltf)
app.command("certify")(certify_component)

# === 🧭 Exécution cockpit
if __name__ == "__main__":
    app()
