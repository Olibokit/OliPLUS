# 📘 cockpit_boot.py — Lanceur typé du système cockpit OliPLUS

import logging
from OliPLUS.core.config.settings import settings
from OliPLUS.cli.oli_cli import app as cockpit_cli
from OliPLUS.dashboard.dashboard_ui import main as launch_dashboard
from OliPLUS.core.sync.SyncEngine import main as sync_engine
from pathlib import Path

# 🔧 Configuration du logging cockpit
logging.basicConfig(level=logging.INFO, format="📘 %(message)s")
logger = logging.getLogger("cockpit_boot")

def check_directories():
    logger.info("📁 Vérification des répertoires cockpit...")
    for path in [settings.LOG_DIR, settings.CACHE_DIR]:
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"📦 Répertoire créé : {path}")
        else:
            logger.info(f"✅ Répertoire existant : {path}")

def launch_components():
    logger.info("\n🚀 Lancement des composants cockpitifiés...")

    try:
        logger.info("🧠 Initialisation du moteur de synchronisation cockpit...")
        sync_engine()
    except Exception as e:
        logger.error(f"❌ Échec SyncEngine : {e}")

    try:
        logger.info("🎨 Ouverture du dashboard cockpit Streamlit...")
        launch_dashboard()
    except Exception as e:
        logger.error(f"❌ Échec dashboard_ui : {e}")

def main():
    logger.info("\n🧭 Démarrage cockpit OliPLUS")
    logger.info(f"🔧 Environnement : {settings.APP_ENV}")
    logger.info(f"🛠️ Mode debug : {'activé' if settings.APP_DEBUG else 'désactivé'}")
    logger.info(f"🌐 Port API cockpit : {settings.API_PORT}")

    check_directories()
    launch_components()

    logger.info("\n📘 Interface CLI cockpitifiée disponible")
    logger.info("💡 Tapez une commande ou utilisez `oli_cli.py list` pour voir les options")

if __name__ == "__main__":
    main()
