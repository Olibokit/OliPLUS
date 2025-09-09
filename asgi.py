import os
import django
from django.core.asgi import get_asgi_application

# 🔧 Configuration du module de settings cockpitifié
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "OIIPLUS.settings")

# 🚀 Initialisation Django
django.setup()

# 🌐 Application ASGI
application = get_asgi_application()
