from typing import Dict, Literal
from rich import print
from rich.table import Table

ApprovalLevel = Dict[str, str]

approval_chain: ApprovalLevel = {
    "demande": "👤 salarié",
    "niveau_1": "👨‍💼 responsable d'équipe",
    "niveau_2": "🧑‍💼 RH",
    "niveau_3": "🧑‍✈️ directeur général"
}

KnownLevels = Literal["demande", "niveau_1", "niveau_2", "niveau_3"]

def print_chain() -> None:
    print("\n[bold blue]🔗 Chaîne de validation cockpit RH[/]\n")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Niveau", style="dim", width=12)
    table.add_column("Acteur", style="cyan")

    for niveau, acteur in approval_chain.items():
        table.add_row(niveau, acteur)

    print(table)

def get_approver_by_level(niveau: str) -> str:
    return approval_chain.get(niveau, "⛔ Niveau inconnu")

def validate_level(niveau: str) -> None:
    acteur = get_approver_by_level(niveau)
    if acteur.startswith("⛔"):
        print(f"[red]❌ Niveau '{niveau}' non reconnu.[/]")
    else:
        print(f"[green]✅ Niveau '{niveau}' validé par :[/] [bold]{acteur}[/]")

def list_approvers() -> None:
    print("\n[bold yellow]📋 Liste des validateurs cockpit[/]")
    for niveau, acteur in approval_chain.items():
        print(f"• [bold]{niveau}[/] → {acteur}")

if __name__ == "__main__":
    print_chain()
    validate_level("niveau_2")
    list_approvers()
