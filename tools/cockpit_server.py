from __future__ import annotations
import os
from typing import TYPE_CHECKING, Any, Callable, cast
import tornado.web

from streamlit import config, file_util
from streamlit.web.server.server_util import (
    allowlisted_origins,
    emit_endpoint_deprecation_notice,
    is_xsrf_enabled,
)

if TYPE_CHECKING:
    from collections.abc import Awaitable, Sequence

# ─── CORS cockpitifié ─────────────────────────────────────────────────────────

def allow_all_cross_origin_requests() -> bool:
    return not config.get_option("server.enableCORS") or config.get_option("global.developmentMode")

def is_allowed_origin(origin: Any) -> bool:
    return isinstance(origin, str) and origin in allowlisted_origins()

# ─── Handlers cockpitifiés ────────────────────────────────────────────────────

class StaticFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path: str, default_filename: str | None = None, reserved_paths: Sequence[str] = ()) -> None:
        self._reserved_paths = reserved_paths
        super().initialize(path, default_filename)

    def set_extra_headers(self, path: str) -> None:
        self.set_header("Cache-Control", "no-cache" if path.endswith(".html") or len(path) == 0 else "public")

    def validate_absolute_path(self, root: str, absolute_path: str) -> str | None:
        try:
            return super().validate_absolute_path(root, absolute_path)
        except tornado.web.HTTPError as e:
            if e.status_code == 404:
                url_path = self.path.replace(os.path.sep, "/")
                if any(url_path.endswith(x) for x in self._reserved_paths):
                    raise
                self.path = self.parse_url_path(self.default_filename or "index.html")
                absolute_path = self.get_absolute_path(self.root, self.path)
                return super().validate_absolute_path(root, absolute_path)
            raise

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        if status_code == 404:
            index_file = os.path.join(file_util.get_static_dir(), "index.html")
            self.render(index_file)
        else:
            super().write_error(status_code, **kwargs)

class _SpecialRequestHandler(tornado.web.RequestHandler):
    def set_default_headers(self) -> None:
        self.set_header("Cache-Control", "no-cache")
        origin = self.request.headers.get("Origin")
        if allow_all_cross_origin_requests():
            self.set_header("Access-Control-Allow-Origin", "*")
        elif is_allowed_origin(origin):
            self.set_header("Access-Control-Allow-Origin", cast("str", origin))

    def options(self) -> None:
        self.set_status(204)
        self.finish()

class HealthHandler(_SpecialRequestHandler):
    def initialize(self, callback: Callable[[], Awaitable[tuple[bool, str]]]) -> None:
        self._callback = callback

    async def get(self) -> None:
        await self.handle_request()

    async def head(self) -> None:
        await self.handle_request()

    async def handle_request(self) -> None:
        if self.request.uri and "_stcore/" not in self.request.uri:
            new_path = "/_stcore/script-health-check" if "script-health-check" in self.request.uri else "/_stcore/health"
            emit_endpoint_deprecation_notice(self, new_path=new_path)

        ok, msg = await self._callback()
        self.set_status(200 if ok else 503)
        self.write(msg)

        if ok and is_xsrf_enabled():
            cookie_kwargs = self.settings.get("xsrf_cookie_kwargs", {})
            self.set_cookie(
                self.settings.get("xsrf_cookie_name", "_streamlit_xsrf"),
                self.xsrf_token,
                **cookie_kwargs,
            )

class HostConfigHandler(_SpecialRequestHandler):
    def initialize(self) -> None:
        self._allowed_origins = _DEFAULT_ALLOWED_MESSAGE_ORIGINS.copy()
        if config.get_option("global.developmentMode"):
            self._allowed_origins.append("http://localhost")

    async def get(self) -> None:
        self.write({
            "allowedOrigins": self._allowed_origins,
            "useExternalAuthToken": False,
            "enableCustomParentMessages": False,
            "enforceDownloadInNewTab": False,
            "metricsUrl": "",
            "blockErrorDialogs": False,
            "resourceCrossOriginMode": None,
        })
        self.set_status(200)

# ─── Origines cockpitifiées ──────────────────────────────────────────────────

_DEFAULT_ALLOWED_MESSAGE_ORIGINS = [
    "https://*.streamlitapp.com",
    "https://share.streamlit.io",
    "https://*.streamlit.run",
    "https://*.streamlit.app",
    "http://localhost",
]
