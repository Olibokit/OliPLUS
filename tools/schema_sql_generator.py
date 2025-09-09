#!/usr/bin/env python
import os
import yaml
from pathlib import Path
from typing import Dict, Any

YAML_PATH = Path("OliPLUS.oliplus_toolchain/schemas/modeles_documents.yaml")
SQL_OUTPUT = Path("sql/generated/oliplus_schema.sql")
SQL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def load_schema(path: Path = YAML_PATH) -> Dict[str, Any]:
    """📥 Charge le schéma YAML des modèles"""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def build_sql_for_model(name: str, model: Dict[str, Any]) -> str:
    """🛠️ Construit le SQL pour un modèle donné"""
    lines = [f"-- ✅ Table `{name}`"]
    table_name = model.get("target", name).lower()
    lines.append(f"CREATE TABLE {table_name} (\n    id SERIAL PRIMARY KEY")

    # 🧬 Champs classiques
    for field, alias in model.get("fields", {}).items():
        lines.append(f"  , {alias} TEXT")

    # 🔗 Relations
    for rel, target in model.get("relations", {}).items():
        fk = f"{rel}_id"
        target_table = target.lower()
        lines.append(f"  , {fk} INTEGER REFERENCES {target_table}(id) ON DELETE CASCADE")

    lines.append(");")

    # 🔐 Contrainte unique
    if "unique_together" in model.get("options", {}):
        cols = ", ".join(model["options"]["unique_together"])
        lines.append(f"CREATE UNIQUE INDEX ON {table_name} ({cols});")

    return "\n".join(lines)

def run() -> None:
    schema = load_schema()
    all_sql = []

    for section_name, section in schema.items():
        for name, model in section.items():
            sql = build_sql_for_model(name, model)
            all_sql.append(sql)

    with SQL_OUTPUT.open("w", encoding="utf-8") as f:
        f.write("\n\n".join(all_sql))

    print(f"🧾 SQL généré dans : {SQL_OUTPUT.resolve()}")

if __name__ == "__main__":
    run()
