import argparse
import sys
import json
import csv
from pathlib import Path
from datetime import datetime

# 🧠 Import cockpitifiés (à adapter selon ton projet)
from classification.service import ClassificationService
from classification.search import advanced_search
from classification.describe import describe_node
from classification.tree import print_tree

def print_tree_flat(nodes):
    for node in nodes:
        chemin = node.nom
        parent = node.parent
        while parent:
            chemin = f"{parent.nom} > {chemin}"
            parent = parent.parent
        print(f"- {node.code} → {chemin}")

def run(args):
    service = ClassificationService(Path(args.yaml))
    try:
        service.load()
    except Exception as e:
        print(f"❌ Erreur de chargement YAML : {e}")
        if not args.no_sys_exit:
            sys.exit(1)
        return

    match args.command:
        case "list":
            print("📚 Liste des catégories :")
            for node in service.list_all_categories():
                print(f"{node.code} → {node.nom}")

        case "tree":
            print("🌳 Arborescence des catégories :\n")
            if args.tree_flat:
                print_tree_flat(service.list_all_categories())
            else:
                print_tree(service.get_tree())

        case "describe":
            if not args.query:
                print("❗ Utilise --query pour fournir un code.")
                if not args.no_sys_exit:
                    sys.exit(1)
                return
            describe_node(service, args.query)
            print("🧾 Description terminée.")

        case "export-json":
            if not args.output:
                print("🚫 L’argument --output est requis.")
                if not args.no_sys_exit:
                    sys.exit(1)
                return
            data = [node.to_dict() for node in service.get_tree()]
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2 if args.json_pretty else None)
            print(f"✅ Export JSON → {args.output}")

        case "search":
            if not args.query:
                print("⚠️ Fournis un mot-clé avec --query")
                if not args.no_sys_exit:
                    sys.exit(1)
                return

            results = advanced_search(
                nodes=service.get_tree(),
                keyword=args.query,
                case_insensitive=args.case_insensitive,
                deep=args.deep,
                max_depth=args.max_depth,
                exact=args.exact
            )

            if not results:
                print(f"🔍 Aucun résultat pour : {args.query}")
                if not args.no_sys_exit:
                    sys.exit(1)
                return

            print(f"🔍 Résultats pour « {args.query} » :\n")
            for r in results:
                print(f"- {r['code']} → {r['chemin']} (niveau {r['profondeur']})")

            if args.codes_only:
                codes = {r['code'] for r in results}
                print("\n🔢 Codes extraits :")
                for code in sorted(codes):
                    print(f"- {code}")

            if args.output:
                Path(args.output).parent.mkdir(parents=True, exist_ok=True)
                suffix = Path(args.output).suffix.lower()

                if suffix == ".csv":
                    with open(args.output, "w", newline="", encoding="utf-8-sig" if args.csv_utf8 else "utf-8") as f:
                        writer = csv.DictWriter(f, fieldnames=["code", "nom", "chemin", "profondeur"])
                        writer.writeheader()
                        writer.writerows(results)
                    print(f"\n📄 Export CSV → {args.output}")

                elif suffix == ".md":
                    with open(args.output, "w", encoding="utf-8") as f:
                        f.write("# 📘 Résultats de recherche – Classification\n\n")
                        for r in results:
                            f.write(f"- **{r['code']}** → {r['chemin']} (niveau {r['profondeur']})\n")
                    print(f"\n📄 Export Markdown → {args.output}")

                else:
                    with open(args.output, "w", encoding="utf-8") as f:
                        json.dump(results, f, ensure_ascii=False, indent=2 if args.json_pretty else None)
                    print(f"\n💾 Export JSON → {args.output}")

            if args.save_search:
                log_path = Path("oliplus_data/logs/search_log.md")
                log_path.parent.mkdir(parents=True, exist_ok=True)
                with log_path.open("a", encoding="utf-8") as f:
                    f.write(f"## 🔎 Recherche : {args.query} ({datetime.now():%Y-%m-%d %H:%M})\n")
                    for r in results:
                        f.write(f"- `{r['code']}` → {r['chemin']}\n")
                    f.write("\n")
                print(f"\n📝 Recherche consignée dans : {log_path}")

def main():
    parser = argparse.ArgumentParser(description="🌐 CLI OliPLUS – Explorateur cockpit de classification")
    parser.add_argument("command", choices=["list", "tree", "export-json", "search", "describe"])
    parser.add_argument("--yaml", default="classification_structure.yaml")
    parser.add_argument("--output")
    parser.add_argument("--query")

    # Options cockpit pour recherche et export
    parser.add_argument("--case-insensitive", action="store_true")
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--max-depth", type=int)
    parser.add_argument("--exact", action="store_true")
    parser.add_argument("--json-pretty", action="store_true")
    parser.add_argument("--csv-utf8", action="store_true")
    parser.add_argument("--codes-only", action="store_true")
    parser.add_argument("--save-search", action="store_true")
    parser.add_argument("--tree-flat", action="store_true", help="Afficher une arborescence aplatie")
    parser.add_argument("--no-sys-exit", action="store_true", help="Désactiver sys.exit (utile pour CI ou tests)")

    args = parser.parse_args()
    try:
        run(args)
    except Exception as e:
        print(f"💥 Erreur inattendue : {e}")
        if not args.no_sys_exit:
            sys.exit(1)

if __name__ == "__main__":
    main()
