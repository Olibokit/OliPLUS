import os
import logging
from inspect import getattr_static, unwrap
from typing import Any, Optional, Iterable

from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.http import Http404, HttpRequest, HttpResponse
from django.template import loader
from django.utils import feedgenerator
from django.utils.encoding import iri_to_uri
from django.utils.http import http_date
from django.utils.timezone import get_default_timezone, is_naive, make_aware
from django.utils.translation import get_language

logger = logging.getLogger(__name__)

def add_domain(domain: str, url: str, secure: bool = False) -> str:
    protocol = "https" if secure else "http"
    if url.startswith("//"):
        return f"{protocol}:{url}"
    elif not url.startswith(("http://", "https://", "mailto:")):
        return iri_to_uri(f"{protocol}://{domain}{url}")
    return url

class FeedDoesNotExist(ObjectDoesNotExist):
    pass

class Feed:
    feed_type = feedgenerator.DefaultFeed  # ou feedgenerator.Atom1Feed

    title_template: Optional[str] = None
    description_template: Optional[str] = None
    language: Optional[str] = None

    def __call__(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            logger.warning("📡 Objet introuvable pour le flux.")
            raise Http404("Objet pour le flux introuvable.")

        feedgen = self.get_feed(obj, request)
        response = HttpResponse(content_type=feedgen.content_type)

        if hasattr(self, "item_pubdate") or hasattr(self, "item_updateddate"):
            try:
                last = feedgen.latest_post_date()
                if last:
                    response.headers["Last-Modified"] = http_date(last.timestamp())
            except Exception as e:
                logger.warning(f"⚠️ Impossible de calculer la date Last-Modified : {e}")

        feedgen.generator = "OliPLUS Cockpit RSS Engine"
        feedgen.write(response, "utf-8")
        return response

    def item_title(self, item: Any) -> str:
        return str(item)

    def item_description(self, item: Any) -> str:
        return str(item)

    def item_link(self, item: Any) -> str:
        if hasattr(item, "get_absolute_url"):
            return item.get_absolute_url()
        elif hasattr(item, "url"):
            return item.url
        raise ImproperlyConfigured(
            f"Ajoute get_absolute_url() ou url à {item.__class__.__name__} — sinon redéfinis item_link()."
        )

    def item_enclosures(self, item: Any) -> list:
        url = self._get_dynamic_attr("item_enclosure_url", item)
        if url:
            return [feedgenerator.Enclosure(
                url=str(url),
                length=str(self._get_dynamic_attr("item_enclosure_length", item)),
                mime_type=str(self._get_dynamic_attr("item_enclosure_mime_type", item)),
            )]
        return []

    def _get_dynamic_attr(self, attname: str, obj: Any, default: Any = None) -> Any:
        attr = getattr(self, attname, default)
        if callable(attr):
            try:
                func = unwrap(attr)
                code = getattr(func, "__code__", None)
                is_static = isinstance(getattr_static(self, func.__name__, None), staticmethod)

                if not code or (not code.co_argcount and not is_static):
                    raise ImproperlyConfigured(f"Feed method `{attname}` doit utiliser `@functools.wraps`.")
                return attr(obj) if code.co_argcount == 2 else attr()
            except Exception as e:
                logger.warning(f"⚠️ Erreur d’attribut dynamique `{attname}` : {e}")
                return default
        return attr

    def feed_extra_kwargs(self, obj: Any) -> dict:
        return {}

    def item_extra_kwargs(self, item: Any) -> dict:
        return {}

    def get_object(self, request: HttpRequest, *args, **kwargs) -> Any:
        return None

    def get_context_data(self, **kwargs) -> dict:
        return {
            "item": kwargs.get("item"),
            "site": kwargs.get("site"),
            "obj": kwargs.get("obj"),
            "request": kwargs.get("request")
        }

    def get_feed(self, obj: Any, request: HttpRequest) -> feedgenerator.SyndicationFeed:
        site = get_current_site(request)
        secure = request.is_secure()
        items = self._get_dynamic_attr("items", obj)

        if not items or not hasattr(items, "__iter__"):
            raise ImproperlyConfigured("items() doit retourner un iterable de contenus.")

        feed = self.feed_type(
            title=self._get_dynamic_attr("title", obj),
            subtitle=self._get_dynamic_attr("subtitle", obj),
            link=add_domain(site.domain, self._get_dynamic_attr("link", obj), secure),
            description=self._get_dynamic_attr("description", obj),
            language=self.language or get_language(),
            feed_url=add_domain(site.domain, self._get_dynamic_attr("feed_url", obj) or request.path, secure),
            **self.feed_extra_kwargs(obj),
        )

        tpl_title = loader.get_template(self.title_template) if self.title_template else None
        tpl_desc = loader.get_template(self.description_template) if self.description_template else None

        for item in items:
            context = self.get_context_data(item=item, site=site, obj=obj, request=request)

            title = tpl_title.render(context, request) if tpl_title else self._get_dynamic_attr("item_title", item)
            desc = tpl_desc.render(context, request) if tpl_desc else self._get_dynamic_attr("item_description", item)
            item_link = add_domain(site.domain, self._get_dynamic_attr("item_link", item), secure)

            pub = self._get_dynamic_attr("item_pubdate", item, None)
            pubdate = make_aware(pub, get_default_timezone()) if pub and is_naive(pub) else pub

            upd = self._get_dynamic_attr("item_updateddate", item, None)
            updated = make_aware(upd, get_default_timezone()) if upd and is_naive(upd) else upd

            feed.add_item(
                title=title,
                link=item_link,
                description=desc,
                unique_id=self._get_dynamic_attr("item_guid", item, item_link),
                unique_id_is_permalink=self._get_dynamic_attr("item_guid_is_permalink", item) or False,
                pubdate=pubdate,
                updateddate=updated,
                enclosures=self.item_enclosures(item),
                **self.item_extra_kwargs(item),
            )
        return feed
