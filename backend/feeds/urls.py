from django.urls import path

# 📰 Flux activés
from backends.feeds.blog import BlogFeed

# 📭 Flux désactivés (à activer si besoin)
# from backends.feeds.newsletter import NewsletterFeed
# from backends.feeds.ventes import VentesFeed

app_name = "feeds"

urlpatterns = [
    path("blog.xml", BlogFeed(), name="blog-feed"),
    # path("newsletter.xml", NewsletterFeed(), name="newsletter-feed"),
    # path("ventes.xml", VentesFeed(), name="ventes-feed"),
]
