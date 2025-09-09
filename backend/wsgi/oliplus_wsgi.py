#!/usr/bin/env python

import os
import sys
import logging
import platform
from pathlib import Path
from typing import Optional
from django.core.wsgi import get_wsgi_application

# 🌍 Configuration Django
DEFAULT_SETTINGS_MODULE = "OliPLUS.settings"
DJANGO_SETTINGS = os.getenv("DJANGO_SETTINGS_MODULE", DEFAULT_SETTINGS_MODULE)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS)

# 🪵 Setup Logging
LOG_LEVEL = os.getenv("WSGI_LOG_LEVEL", "INFO").upper()
LOG_FILE = os.getenv("WSGI_LOG_FILE", "/tmp/oliplus_wsgi.log")

# 🔐 Sécurisation du chemin de log
try:
    LOG_PATH = Path(LOG_FILE).parent
    LOG_PATH.mkdir(parents=True, exist_ok=True)
except Exception as e:
    print(f"❌ Impossible de créer le dossier de log : {LOG_PATH}")
    sys.exit(1)

def configure_logging(log_file: str, level: str = "INFO") -> None:
    if not logging.getLogger().hasHandlers():
        logging.basicConfig(
            level=getattr(logging, level, logging.INFO),
            format="%(asctime)s [WSGI] [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stderr),
            ],
        )

# 🔧 Initialisation du logging
configure_logging(LOG_FILE, LOG_LEVEL)
logging.info(f"🔧 WSGI initialisé → settings = '{DJANGO_SETTINGS}', log = '{LOG_FILE}'")
logging.info(f"🖥️ Plateforme : {platform.system()} {platform.release()} | Python {platform.python_version()}")

# 🚀 Initialisation de l'application Django
try:
    application = get_wsgi_application()
    logging.info("✅ Application WSGI chargée avec succès (OliPLUS)")
except Exception as e:
    logging.critical("❌ Erreur critique lors du chargement WSGI", exc_info=True)
    raise
