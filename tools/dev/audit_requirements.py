from pathlib import Path
from requirement import ParsedRequirement, InvalidRequirement
from rich import print
from rich.console import Console
from rich.table import Table

console = Console()


def validate_file(path: str, python_version: str = "3.12", show_skipped: bool = False) -> None:
    """
    Valide un fichier de dépendances ligne par ligne.

    Args:
        path (str): Chemin vers le fichier requirements.txt.
        python_version (str): Version cible de Python pour la compatibilité.
        show_skipped (bool): Affiche les lignes ignorées (commentaires, vides).
    """
    file = Path(path)

    if not file.exists():
        print(f"[red]❌ Fichier introuvable :[/red] [bold]{path}[/bold]")
        return

    print(f"\n[cyan]🔍 Audit typé cockpit du fichier :[/cyan] [bold]{file.name}[/bold]\n")

    lines = file.read_text(encoding="utf-8").splitlines()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ligne", justify="right")
    table.add_column("Statut")
    table.add_column("Package")
    table.add_column("Extras")
    table.add_column("Marker")
    table.add_column("Compatible")

    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            if show_skipped:
                table.add_row(f"{i}", "[dim]⏭️ Ignorée[/dim]", "[dim italic]—[/dim italic]", "—", "—", "—")
            continue

        try:
            req = ParsedRequirement(stripped)
            compatible = req.is_compatible(python_version)
            status = "[green]✅[/green]" if compatible else "[yellow]⚠️[/yellow]"
            table.add_row(
                f"{i}",
                status,
                f"[bold]{req.name}[/bold]",
                req.extras or "—",
                req.marker or "—",
                str(compatible)
            )
        except InvalidRequirement as e:
            table.add_row(
                f"{i}",
                "[red]❌[/red]",
                f"[italic]{stripped}[/italic]",
                "—",
                "—",
                f"[red]{e}[/red]"
            )

    console.print(table)


# 📦 CLI wrapper
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="🧰 Audit cockpit des requirements")
    parser.add_argument("path", help="Chemin du fichier requirements.txt")
    parser.add_argument("--python", default="3.12", help="Version cible de Python (défaut: 3.12)")
    parser.add_argument("--show-skipped", action="store_true", help="Afficher les lignes ignorées")
    args = parser.parse_args()

    validate_file(args.path, python_version=args.python, show_skipped=args.show_skipped)
