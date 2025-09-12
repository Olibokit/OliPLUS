from .base import *

# 🐞 Mode debug activé pour développement local
DEBUG = True

# 🌍 Hôtes autorisés pendant le dev (IP, localhost, nom réseau local)
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",           # utile avec Docker ou réseaux partagés
    "testserver",        # utilisé par Django lors des tests unitaires
]

# 🔄 CORS pour tests frontend local
CORS_ALLOWED_ORIGINS = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# 📧 Email backend pour affichage en console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# 🧪 Ajout de debug toolbar (optionnel mais utile)
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

INTERNAL_IPS = ["127.0.0.1"]

# 📂 Fichiers statiques et médias en local
STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"
