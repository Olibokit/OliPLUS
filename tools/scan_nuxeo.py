import yaml
import typer
from pathlib import Path
from typing import Dict, List, Optional

app = typer.Typer()

def classify_path(path: Path) -> str:
    parts = set(path.parts)
    if "templates" in parts:
        return "templates"
    elif "conf" in parts:
        return "conf"
    elif "packages" in parts:
        return "packages"
    elif "bin" in parts or "lib" in parts:
        return "binaries"
    elif "log" in parts or "logs" in parts:
        return "logs"
    return "others"

@app.command()
def scan_nuxeo(
    path: Path = typer.Option(Path("/opt/nuxeo/server"), "--path", "-p", help="📁 Dossier racine Nuxeo à scanner"),
    ext: Optional[str] = typer.Option(None, "--ext", "-e", help="🔍 Extension à filtrer (ex: .xml, .properties)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="🧪 Simulation sans écriture du fichier YAML")
) -> None:
    """
    🔍 Scanne le dossier Nuxeo et classe les chemins par catégorie cockpit.
    """
    if not path.exists():
        typer.secho(f"❌ Dossier introuvable : {path}", fg="red")
        raise typer.Exit(code=1)

    summary: Dict[str, List[str]] = {
        "templates": [],
        "conf": [],
        "packages": [],
        "binaries": [],
        "logs": [],
        "others": []
    }

    for item in path.rglob("*"):
        if not item.exists():
            continue
        if ext and item.is_file() and not item.name.endswith(ext):
            continue

        category = classify_path(item)
        summary[category].append(str(item))

    if dry_run:
        typer.secho("🧪 Mode simulation activé — aucun fichier écrit", fg="yellow")
    else:
        output_path = Path("cockpit_data/scans/nuxeo_scan.yaml")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as f:
            yaml.dump(summary, f, sort_keys=False, allow_unicode=True)
        typer.secho(f"✅ Scan Nuxeo cockpit terminé → {output_path}", fg="green")

    typer.echo("\n📊 Statistiques :")
    for category, items in summary.items():
        typer.echo(f" - {category}: {len(items)} élément(s)")

if __name__ == "__main__":
    app()
