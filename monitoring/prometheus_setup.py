import os
import shutil
import tempfile
import logging
import atexit
from typing import Optional

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Ajout d’un handler par défaut si aucun configuré (utile en CLI standalone)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(handler)

def configure_prometheus_multiproc_dir(force_tmp: bool = False) -> str:
    """
    ⚙️ Configure le répertoire multi-process pour Prometheus selon l’environnement.
    Peut forcer un dossier temporaire via force_tmp=True.
    """
    env_path = os.getenv("PROMETHEUS_MULTIPROC_DIR")

    if env_path and not force_tmp:
        try:
            os.makedirs(env_path, mode=0o770, exist_ok=True)
            logger.info(f"[cockpit] Répertoire Prometheus existant utilisé : {env_path}")
            return env_path
        except Exception as e:
            logger.warning(f"[cockpit] Échec création répertoire défini dans l’environnement : {e}")

    try:
        tmp_path = tempfile.mkdtemp(prefix="prometheus-stats-")
        os.environ["PROMETHEUS_MULTIPROC_DIR"] = tmp_path
        logger.info(f"[cockpit] Répertoire Prometheus temporaire créé : {tmp_path}")
        return tmp_path
    except Exception as e:
        logger.error(f"[cockpit] Échec de génération du répertoire temporaire Prometheus : {e}")
        raise

def delete_prometheus_multiproc_dir(dir_path: Optional[str]) -> None:
    """
    🧹 Supprime le répertoire temporaire Prometheus si généré automatiquement.
    """
    if dir_path and dir_path.startswith(tempfile.gettempdir()):
        try:
            shutil.rmtree(dir_path)
            logger.info(f"[cockpit] Répertoire temporaire Prometheus supprimé : {dir_path}")
        except Exception as e:
            logger.warning(f"[cockpit] Échec suppression du répertoire : {dir_path} — {e}")
    else:
        logger.debug(f"[cockpit] Aucun nettoyage requis pour : {dir_path}")

# ⏳ Initialisation automatique + nettoyage à la fermeture du processus
_prom_dir: str = configure_prometheus_multiproc_dir()
atexit.register(delete_prometheus_multiproc_dir, _prom_dir)
