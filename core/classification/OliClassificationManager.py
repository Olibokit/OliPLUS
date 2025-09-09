import os
import json
import yaml
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from pathlib import Path

@dataclass
class OliClassificationCategory:
    code: str
    nom: str
    description: Optional[str] = None
    parent_code: Optional[str] = None
    sous_categories: List['OliClassificationCategory'] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "nom": self.nom,
            "description": self.description,
            "parent_code": self.parent_code,
            "sous_categories": [sub.to_dict() for sub in self.sous_categories]
        }

@dataclass
class OliDocType:
    nom: str
    code_classification: str
    id: Optional[str] = None
    description: Optional[str] = None

@dataclass
class OliDoc:
    titre: str
    code_classification: str
    id: Optional[str] = None

CLASSIFICATION_FILE = "classification_structure.yaml"
OUTPUT_JSON_FILE = "classification_structure.json"

class OliClassificationManager:
    def __init__(self):
        self.categories_by_code: Dict[str, OliClassificationCategory] = {}
        self.root_categories: List[OliClassificationCategory] = []

    def load_from_yaml(self, file_path: str):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "classification_plan" not in data:
                print(f"❌ Erreur : clé 'classification_plan' manquante dans '{file_path}'.")
                return

            for cat_data in data["classification_plan"]:
                self._build_category_tree(cat_data, None)

            for category in self.categories_by_code.values():
                if category.parent_code:
                    parent = self.categories_by_code.get(category.parent_code)
                    if parent:
                        parent.sous_categories.append(category)
                    else:
                        print(f"⚠️ Parent introuvable pour '{category.code}' → '{category.parent_code}'")
                else:
                    self.root_categories.append(category)

            for cat in self.categories_by_code.values():
                cat.sous_categories.sort(key=lambda c: c.code)
            self.root_categories.sort(key=lambda c: c.code)

            print(f"✅ {len(self.categories_by_code)} catégories chargées avec succès.")

        except FileNotFoundError:
            print(f"❌ Fichier introuvable : {file_path}")
        except yaml.YAMLError as e:
            print(f"❌ Erreur de parsing YAML : {e}")

    def _build_category_tree(self, cat_data: Dict[str, Any], parent_code: Optional[str]):
        code = cat_data["code"]
        category = OliClassificationCategory(
            code=code,
            nom=cat_data["nom"],
            description=cat_data.get("description"),
            parent_code=parent_code
        )
        self.categories_by_code[code] = category

        for sub in cat_data.get("sous_categories", []):
            self._build_category_tree(sub, code)

    def get_root_categories(self) -> List[OliClassificationCategory]:
        return self.root_categories

    def get_category_by_code(self, code: str) -> Optional[OliClassificationCategory]:
        return self.categories_by_code.get(code)

    def search_category(self, query: str) -> List[OliClassificationCategory]:
        q = query.lower()
        return sorted([
            cat for cat in self.categories_by_code.values()
            if q in cat.nom.lower() or q in cat.code.lower()
        ], key=lambda x: x.code)

    def export_to_json(self, file_path: str):
        if not self.root_categories:
            print("⚠️ Aucune catégorie racine à exporter.")
            return
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                [cat.to_dict() for cat in self.root_categories],
                f,
                ensure_ascii=False,
                indent=2
            )
        print(f"📤 Export JSON terminé : {file_path}")

if __name__ == "__main__":
    manager = OliClassificationManager()
    manager.load_from_yaml(CLASSIFICATION_FILE)

    print("\n📁 Catégories racines :")
    for cat in manager.get_root_categories():
        print(f"- {cat.code}: {cat.nom} ({cat.description})")

    print("\n🔍 Résultats de recherche 'ressources' :")
    results = manager.search_category("ressources")
    for r in results:
        print(f"  - {r.code}: {r.nom}")

    print("\n📄 Création d’un document exemple :")
    admin = manager.get_category_by_code("1000")
    if admin:
        doc = OliDoc(titre="Rapport Annuel 2024", code_classification=admin.code)
        print(f"  > Document : {doc.titre}, classé sous : {doc.code_classification}")

    manager.export_to_json(OUTPUT_JSON_FILE)
