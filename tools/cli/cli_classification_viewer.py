import argparse
import json
import csv
import sys
from pathlib import Path
from classification_service import ClassificationService


def afficher_liste(service: ClassificationService) -> None:
    print("📚 Liste des catégories (code → nom) :\n")
    for node in service.list_all_categories():
        print(f"{node.code} → {node.nom}")


def afficher_arborescence(service: ClassificationService, code: str | None = None) -> None:
    def print_tree(nodes, indent: int = 0) -> None:
        for node in nodes:
            print("  " * indent + f"- {node.code} — {node.nom}")
            print_tree(node.children, indent + 1)

    if code:
        node = service.find_by_code(code)
        if node:
            print(f"🌳 Descendance de '{code}' — {node.nom} :\n")
            print_tree([node])
        else:
            print(f"❌ Code introuvable : {code}")
            sys.exit(1)
    else:
        print("🌳 Arborescence complète :\n")
        print_tree(service.get_tree())


def exporter(service: ClassificationService, output_path: Path, fmt: str = "json") -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = [node.to_dict() for node in service.get_tree()]

    if fmt == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON exporté → {output_path}")
    elif fmt == "csv":
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["code", "nom", "parent"])
            writer.writeheader()
            for node in service.list_all_categories():
                writer.writerow({
                    "code": node.code,
                    "nom": node.nom,
                    "parent": node.parent.code if node.parent else ""
                })
        print(f"✅ CSV exporté → {output_path}")
    else:
        print(f"❌ Format non pris en charge : {fmt}")
        sys.exit(1)


def valider_structure(service: ClassificationService) -> None:
    try:
        tree = service.get_tree()
        print(f"✅ Structure valide — {len(tree)} racines détectées.")
    except Exception as e:
        print(f"❌ Erreur de validation : {e}")
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="🛠️ CLI cockpit — Classification Oliplus")
    parser.add_argument("command", choices=["list", "tree", "export", "validate"], help="Commande à exécuter")
    parser.add_argument("--yaml", default="classification_structure.yaml", help="Chemin vers le fichier YAML")
    parser.add_argument("--output", help="Fichier de sortie (.json ou .csv)")
    parser.add_argument("--format", choices=["json", "csv"], default="json", help="Format de sortie")
    parser.add_argument("--code", help="Code de départ pour afficher une branche précise")

    args = parser.parse_args()

    try:
        service = ClassificationService(Path(args.yaml))
        service.load()
    except Exception as e:
        print(f"❌ Erreur lors du chargement YAML : {e}")
        sys.exit(1)

    match args.command:
        case "list":
            afficher_liste(service)
        case "tree":
            afficher_arborescence(service, code=args.code)
        case "export":
            if not args.output:
                print("❌ --output requis pour 'export'")
                sys.exit(1)
            exporter(service, Path(args.output), fmt=args.format)
        case "validate":
            valider_structure(service)


if __name__ == "__main__":
    main()
