import yaml
from OliPLUS.OliPLUS.oliplus_toolchain.OliPLUS.oliplus_models import OliDocType
from pathlib import Path

class ClassificationService:
    def __init__(self, yaml_file: str | Path):
        self.yaml_file = Path(yaml_file)
        self.categories: list[OliDocType] = []
        self._loaded = False

    def load(self, force_reload: bool = False):
        """Charge et parse le YAML cockpit en OliDocType (avec validation)."""
        if self._loaded and not force_reload:
            return

        if not self.yaml_file.exists():
            raise FileNotFoundError(f"Fichier YAML introuvable: {self.yaml_file}")

        with self.yaml_file.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict) or "types_documentaires" not in data:
            raise ValueError("YAML invalide — clé 'types_documentaires' absente ou mal formée.")

        self.categories.clear()
        for idx, item in enumerate(data.get("types_documentaires", []), start=1):
            doc_type = OliDocType(
                id=1000 + idx,
                nom=item.get("nom", f"Type_{idx}"),
                description=item.get("description", ""),
                uuid=item.get("uuid", f"auto-{idx}")
            )
            self.categories.append(doc_type)

        self._loaded = True

    def list_all_categories(self) -> list[OliDocType]:
        """Retourne la liste typée des catégories cockpit."""
        if not self._loaded:
            self.load()
        return self.categories

    def as_dicts(self) -> list[dict]:
        """Expose les catégories en dictionnaires JSON-ready."""
        return [
            {
                "id": cat.id,
                "nom": cat.nom,
                "description": cat.description,
                "uuid": cat.uuid
            } for cat in self.list_all_categories()
        ]
