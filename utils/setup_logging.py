import json
import logging
import logging.config
from pathlib import Path

def setup_logging(config_path: str = "config/logging_config.json") -> None:
    """
    Charge et applique la configuration logging cockpit.
    Si le fichier est absent ou invalide, utilise une configuration par défaut.
    """
    config_file = Path(config_path)
    logger = logging.getLogger("cockpit")

    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
            if isinstance(config, dict):
                logging.config.dictConfig(config)
                logger.debug(f"[cockpit] Logging configuré via '{config_path}'")
            else:
                raise ValueError("Format de configuration invalide (doit être un dict)")
        except Exception as e:
            logging.basicConfig(level=logging.INFO)
            logger.warning(f"[cockpit] Erreur chargement config logging : {e}")
    else:
        logging.basicConfig(level=logging.INFO)
        logger.warning(f"[cockpit] Fichier de config logging introuvable : {config_path}")
