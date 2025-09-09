import yaml
from OliPLUS.OliPLUS.oliplus_models import OliMetaType

def import_meta_types(path: Path) -> List[OliMetaType]:
    """
    🧬 Importe les types de métadonnées depuis un fichier YAML.
    Chaque entrée doit contenir : id, label, uuid (optionnel).
    """
    if not path.exists():
        raise FileNotFoundError(f"🚫 Fichier YAML non trouvé : {path}")
    
    try:
        with path.open("r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
            if not isinstance(raw_data, list):
                raise ValueError(f"⚠️ Format inattendu dans {path.name} (attendu : liste)")
    except yaml.YAMLError as e:
        logger.error(f"❌ Erreur YAML dans {path.name} : {e}")
        raise

    types: List[OliMetaType] = []
    for entry in raw_data:
        if not entry.get("id") or not entry.get("label"):
            logger.warning(f"⚠️ Type ignoré : entrée incomplète {entry}")
            continue

        meta_type = OliMetaType(
            id=entry["id"],
            nom=entry["label"],
            uuid=entry.get("uuid")
        )
        types.append(meta_type)

    logger.info(f"🧬 {len(types)} types de métadonnées importés depuis YAML.")
    return types
