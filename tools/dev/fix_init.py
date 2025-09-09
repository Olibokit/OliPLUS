import os
from pathlib import Path
from typing import Set, List, Dict

import typer

app = typer.Typer()

EXCLUDES: Set[str] = {
    "__pycache__", ".git", ".venv", "venv", "env", "node_modules", ".mypy_cache"
}

def should_exclude(dir_name: str) -> bool:
    return dir_name in EXCLUDES

def should_create_init(files: List[str]) -> bool:
    return "__init__.py" not in files and any(f.endswith(".py") for f in files)

@app.command()
def fix_init(
    path: str = typer.Argument(".", help="📁 Chemin racine à scanner"),
    dry: bool = typer.Option(False, help="🧪 Mode simulation (aucune écriture)"),
    quiet: bool = typer.Option(False, help="🔇 Aucune sortie console"),
    docstring: bool = typer.Option(False, help="📘 Ajoute un commentaire dans les __init__.py créés"),
    summary: bool = typer.Option(False, help="📊 Affiche les dossiers modifiés en résumé")
) -> None:
    """
    🔧 Ajoute les __init__.py manquants dans les dossiers Python (hors exclusions).
    """
    total_created = 0
    modified_dirs: Dict[str, str] = {}

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if not should_exclude(d)]
        if should_create_init(files):
            init_path = Path(root) / "__init__.py"
            if dry:
                if not quiet:
                    typer.echo(f"🧪 Manquant : {init_path}")
                modified_dirs[root] = "🧪 Simulation"
            else:
                try:
                    with init_path.open("w", encoding="utf-8") as f:
                        if docstring:
                            f.write("# Auto-généré pour déclarer ce dossier comme package Python\n")
                    if not quiet:
                        typer.echo(f"✅ Créé : {init_path}")
                    modified_dirs[root] = "✅ Créé"
                    total_created += 1
                except Exception as e:
                    typer.secho(f"❌ Erreur lors de la création de {init_path}: {e}", fg="red")

    if not quiet:
        typer.secho(
            f"\n📦 Résultat : {total_created} fichier(s) __init__.py {'seraient ' if dry else ''}ajouté(s)",
            fg="green" if not dry else "yellow"
        )

    if summary and modified_dirs:
        typer.echo("\n📊 Dossiers modifiés :")
        for folder, status in modified_dirs.items():
            typer.echo(f" - {folder}: {status}")

if __name__ == "__main__":
    app()
