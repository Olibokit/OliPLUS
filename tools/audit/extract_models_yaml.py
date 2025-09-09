# 📘 extract_models_yaml.py — Extraction typée des modèles Django cockpitifiés

import re
import yaml
import typer
from pathlib import Path
from datetime import datetime

app = typer.Typer(help="🧩 Outil cockpit pour extraire les modèles Django en YAML")

FIELD_REGEX = re.compile(r'^\s*(\w+)\s*=\s*models\.(\w+)\((.*)\)')
EXCLUDED_DIRS = {"migrations", "__pycache__"}
PROJECT_ROOT = Path(__file__).resolve().parents[2]

def parse_field_args(raw: str) -> dict:
    args = {}
    for arg in raw.split(","):
        if "=" in arg:
            key, val = arg.split("=", 1)
            args[key.strip()] = val.strip()
    return args

def parse_model_def(block: list[str]) -> dict:
    fields = {}
    for line in block:
        match = FIELD_REGEX.match(line)
        if match:
            name, ftype, raw_args = match.groups()
            args = parse_field_args(raw_args)
            is_relation = ftype in {'ForeignKey', 'ManyToManyField', 'OneToOneField'}
            args["is_relation"] = is_relation
            if is_relation:
                args["related_to"] = raw_args.split(',')[0].strip().strip("'\"")
            fields[name] = {
                "type": ftype,
                "args": args
            }
    return {
        "fields": fields,
        "nb_fields": len(fields),
        "relations": [name for name, field in fields.items() if field["args"].get("is_relation")]
    }

def analyze_file(file_path: Path) -> dict:
    models = {}
    try:
        lines = file_path.read_text(encoding="utf-8").splitlines()
        block, model_name = [], None
        for line in lines:
            if line.startswith("class ") and "models.Model" in line:
                if model_name and block:
                    models[model_name] = parse_model_def(block)
                block = []
                model_name = line.split("class ")[1].split("(")[0].strip()
            elif model_name:
                block.append(line)
        if model_name and block:
            models[model_name] = parse_model_def(block)
    except Exception as e:
        print(f"⚠️ Erreur lecture fichier {file_path}: {e}")
    return models

@app.command()
def run(
    apps: list[str] = typer.Option(..., help="Liste des apps Django à analyser"),
    output: str = typer.Option("output/models_summary.yaml", help="Chemin du fichier YAML de sortie")
):
    """
    🧪 Analyse les modèles Django et exporte un résumé typé en YAML.
    """
    summary = {}
    total_models = 0

    for app_name in apps:
        app_dir = PROJECT_ROOT / "apps" / app_name
        if not app_dir.exists():
            print(f"🚫 Dossier introuvable : {app_dir}")
            continue

        py_files = [f for f in app_dir.rglob("*.py") if not any(ex in f.parts for ex in EXCLUDED_DIRS)]
        app_models = {}

        for file in py_files:
            models = analyze_file(file)
            if models:
                for model, content in models.items():
                    content["source_file"] = str(file.relative_to(app_dir))
                    print(f"📘 Modèle détecté : {model} ({content['nb_fields']} champs)")
                app_models[str(file.relative_to(app_dir))] = models
                total_models += len(models)

        if app_models:
            summary[app_name] = app_models
            print(f"📦 Modèles dans `{app_name}` → {sum(len(m) for m in app_models.values())}")
        else:
            print(f"🫥 Aucun modèle trouvé dans `{app_name}`.")

    if summary:
        out_path = PROJECT_ROOT / output
        enriched_summary = {
            "_meta": {
                "timestamp": datetime.now().isoformat(),
                "source": "extract_models_yaml",
                "nb_apps": len(summary),
                "nb_total_models": total_models
            },
            "apps": summary
        }
        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                yaml.dump(enriched_summary, f, sort_keys=False, allow_unicode=True, indent=2)
            print(f"\n✅ Résumé cockpit enrichi → {out_path}")
        except Exception as e:
            print(f"❌ Erreur export YAML : {e}")
    else:
        print("🫥 Aucun contenu exportable.")

if __name__ == "__main__":
    app()
