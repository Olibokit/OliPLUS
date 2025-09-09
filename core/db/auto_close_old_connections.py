import logging
import threading
import traceback
from contextlib import ContextDecorator
from django.conf import settings
from django.db import close_old_connections

logger = logging.getLogger("db.connection.guard")
thread_locals = threading.local()


class AutoCloseOldConnections(ContextDecorator):
    """Ensures old DB connections are closed before execution."""

    def __enter__(self):
        close_old_connections()
        return self

    def __exit__(self, *exc):
        return False


class DebugAutoCloseOldConnections(AutoCloseOldConnections):
    """Debug version with depth tracking and stack trace logging."""

    def __enter__(self):
        depth = getattr(thread_locals, "auto_close_connections_depth", 0) + 1
        thread_locals.auto_close_connections_depth = depth
        logger.debug(f"🔍 Entered auto-close context (depth {depth})")
        return super().__enter__()

    def __exit__(self, *exc):
        depth = getattr(thread_locals, "auto_close_connections_depth", 1) - 1
        thread_locals.auto_close_connections_depth = depth
        logger.debug(f"✅ Exited auto-close context (depth {depth})")
        return False


class CheckCloseConnectionsHandler(logging.Handler):
    """Warns if DB access occurs outside of auto-close context."""

    def emit(self, record):
        if getattr(thread_locals, "auto_close_connections_depth", 0) <= 0:
            logger.warning(
                "⚠️ DB access outside auto_close_old_connections context.\nTraceback:\n%s",
                "".join(traceback.format_stack(limit=10)),
            )


# Choose implementation based on DEBUG mode
auto_close_old_connections: type[AutoCloseOldConnections]

if settings.DEBUG:
    logger.debug("🛠️ Using debug version of auto_close_old_connections")
    auto_close_old_connections = DebugAutoCloseOldConnections

    db_logger = logging.getLogger("django.db.backends")
    db_logger.setLevel(logging.DEBUG)
    db_logger.addHandler(CheckCloseConnectionsHandler(level=logging.DEBUG))
else:
    auto_close_old_connections = AutoCloseOldConnections

__all__ = ("auto_close_old_connections",)
