from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 🧭 Modules Django cockpit à inclure
APP_MODULES = [
    "apps.affiliations",
    "apps.auteurs",
    "apps.common",
    "apps.contrats",
    "apps.devis",
    "apps.finances",
    "apps.formats",
    "apps.fournisseurs",
    "apps.illustrateurs",
    "apps.inventaire",
    "apps.livres",
    "apps.users",
    "apps.ventes",
    "apps.password_reset",   # 🔐 Réinitialisation mot de passe
    "apps.monitoring",       # 🩺 Monitoring cockpit (nouveau)
]

# ✨ Modules cockpit externes ou services
EXTERNAL_MODULES = [
    "backends.feeds",        # 📡 Flux RSS / Atom
    "backends.api",          # 🔌 API cockpit REST/GraphQL
    "backends.analytics",    # 📊 Analytics cockpit
]

urlpatterns = [
    path("admin/", admin.site.urls),

    # 🧩 Chargement modulaire des apps cockpit
    *[path(f"{mod.split('.')[-1]}/", include(f"{mod}.routes")) for mod in APP_MODULES],

    # 🔗 Intégration des modules externes
    *[path(f"{mod.split('.')[-1]}/", include(f"{mod}.routes")) for mod in EXTERNAL_MODULES],

    # 🌐 Page racine cockpit
    path("", include("apps.common.routes")),
]

# 📁 Gestion des fichiers médias en mode DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
