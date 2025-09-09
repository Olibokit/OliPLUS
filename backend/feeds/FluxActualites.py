from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.timezone import localtime
from django.utils.html import strip_tags
from django.contrib.sites.models import Site
from django.utils.text import Truncator

from .feeds.base import Feed
from .models import Actualite


class FluxActualites(Feed):
    """
    📰 Flux RSS des actualités éditoriales et annonces de la plateforme OliPLUS.
    Génère les 15 dernières publications visibles publiquement.
    """
    feed_type = Rss201rev2Feed
    title = "Actualités OliPLUS"
    link = "/actualites/"
    description = "Les dernières publications éditoriales et annonces importantes."
    language = "fr"
    copyright = "© 2025 OliPLUS"
    ttl = 60  # ⏱️ Durée en minutes avant rafraîchissement

    def items(self):
        return Actualite.objects.filter(publique=True).order_by("-date_publication")[:15]

    def item_title(self, item):
        return item.titre or f"Actualité #{item.pk}"

    def item_description(self, item):
        contenu = item.contenu_html or getattr(item, "resume", "") or item.titre
        texte = strip_tags(contenu)
        return Truncator(texte).chars(500, truncate="...") if texte else "Actualité sans description."

    def item_pubdate(self, item):
        return localtime(item.date_publication)

    def item_author_name(self, item):
        auteur = getattr(item, "auteur", None)
        if auteur and hasattr(auteur, "nom_complet"):
            return auteur.nom_complet
        return "Équipe OliPLUS"

    def item_link(self, item):
        try:
            url = item.get_absolute_url()
        except Exception:
            url = f"/actualites/{getattr(item, 'slug', item.pk)}/"

        # Ajoute le domaine si disponible
        site = Site.objects.get_current()
        return f"https://{site.domain}{url}"
