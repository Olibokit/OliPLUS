import base64
import pickle
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT, BaseCache
from django.db import DatabaseError, connections, models, router, transaction
from django.utils.timezone import now as tz_now

logger = logging.getLogger(__name__)


class Options:
    """
    Simule la classe _meta d’un modèle Django pour permettre le routage DB.
    """

    def __init__(self, table: str):
        self.db_table = table
        self.app_label = "django_cache"
        self.model_name = "cacheentry"
        self.verbose_name = "cache entry"
        self.verbose_name_plural = "cache entries"
        self.object_name = "CacheEntry"
        self.abstract = False
        self.managed = True
        self.proxy = False
        self.swapped = False


class BaseDatabaseCache(BaseCache):
    def __init__(self, table: str, params: Dict[str, Any]):
        super().__init__(params)
        self._table = table

        class CacheEntry:
            _meta = Options(table)

        self.cache_model_class = CacheEntry


class DatabaseCache(BaseDatabaseCache):
    """
    Backend de cache Django utilisant une base de données SQL.
    """

    pickle_protocol = pickle.HIGHEST_PROTOCOL

    def get(self, key: str, default: Optional[Any] = None, version: Optional[int] = None) -> Any:
        return self.get_many([key], version).get(key, default)

    def get_many(self, keys: List[str], version: Optional[int] = None) -> Dict[str, Any]:
        if not keys:
            return {}

        key_map = {
            self.make_and_validate_key(key, version=version): key for key in keys
        }

        db = router.db_for_read(self.cache_model_class)
        connection = connections[db]
        quote_name = connection.ops.quote_name
        table = quote_name(self._table)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT {quote_name('cache_key')}, {quote_name('value')}, {quote_name('expires')} "
                    f"FROM {table} WHERE {quote_name('cache_key')} IN ({', '.join(['%s'] * len(key_map))})",
                    list(key_map),
                )
                rows = cursor.fetchall()
        except DatabaseError as e:
            logger.warning(f"Database error during get_many: {e}")
            return {}

        result = {}
        expired_keys = []
        expression = models.Expression(output_field=models.DateTimeField())
        converters = connection.ops.get_db_converters(expression) + expression.get_db_converters(connection)

        for key, value, expires in rows:
            for converter in converters:
                expires = converter(expires, expression, connection)
            if expires < tz_now():
                expired_keys.append(key)
            else:
                value = connection.ops.process_clob(value)
                value = pickle.loads(base64.b64decode(value.encode()))
                result[key_map.get(key)] = value

        self._base_delete_many(expired_keys)
        return result

    def set(self, key: str, value: Any, timeout: int = DEFAULT_TIMEOUT, version: Optional[int] = None) -> bool:
        return self._base_set("set", self.make_and_validate_key(key, version), value, timeout)

    def add(self, key: str, value: Any, timeout: int = DEFAULT_TIMEOUT, version: Optional[int] = None) -> bool:
        return self._base_set("add", self.make_and_validate_key(key, version), value, timeout)

    def touch(self, key: str, timeout: int = DEFAULT_TIMEOUT, version: Optional[int] = None) -> bool:
        return self._base_set("touch", self.make_and_validate_key(key, version), None, timeout)

    def _base_set(self, mode: str, key: str, value: Optional[Any], timeout: int = DEFAULT_TIMEOUT) -> bool:
        timeout = self.get_backend_timeout(timeout)
        db = router.db_for_write(self.cache_model_class)
        connection = connections[db]
        quote_name = connection.ops.quote_name
        table = quote_name(self._table)

        now = tz_now().replace(microsecond=0)
        exp = datetime.max if timeout is None else datetime.fromtimestamp(timeout, timezone.utc if settings.USE_TZ else None)
        exp = exp.replace(microsecond=0)

        pickled = pickle.dumps(value, self.pickle_protocol) if value is not None else b""
        b64encoded = base64.b64encode(pickled).decode("latin1")

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT {quote_name('cache_key')}, {quote_name('expires')} FROM {table} WHERE {quote_name('cache_key')} = %s", [key])
                result = cursor.fetchone()

                current_expires = None
                if result:
                    current_expires = result[1]
                    expression = models.Expression(output_field=models.DateTimeField())
                    for converter in connection.ops.get_db_converters(expression) + expression.get_db_converters(connection):
                        current_expires = converter(current_expires, expression, connection)

                exp = connection.ops.adapt_datetimefield_value(exp)

                if result and mode == "touch":
                    cursor.execute(f"UPDATE {table} SET {quote_name('expires')} = %s WHERE {quote_name('cache_key')} = %s", [exp, key])
                elif result and (mode == "set" or (mode == "add" and current_expires < now)):
                    cursor.execute(
                        f"UPDATE {table} SET {quote_name('value')} = %s, {quote_name('expires')} = %s WHERE {quote_name('cache_key')} = %s",
                        [b64encoded, exp, key],
                    )
                elif mode != "touch":
                    cursor.execute(
                        f"INSERT INTO {table} ({quote_name('cache_key')}, {quote_name('value')}, {quote_name('expires')}) VALUES (%s, %s, %s)",
                        [key, b64encoded, exp],
                    )
                else:
                    return False
        except DatabaseError as e:
            logger.warning(f"Database error during {mode}: {e}")
            return False
        return True

    def delete(self, key: str, version: Optional[int] = None) -> bool:
        return self._base_delete_many([self.make_and_validate_key(key, version)])

    def delete_many(self, keys: List[str], version: Optional[int] = None) -> None:
        validated_keys = [self.make_and_validate_key(key, version) for key in keys]
        self._base_delete_many(validated_keys)

    def _base_delete_many(self, keys: List[str]) -> bool:
        if not keys:
            return False

        db = router.db_for_write(self.cache_model_class)
        connection = connections[db]
        quote_name = connection.ops.quote_name
        table = quote_name(self._table)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"DELETE FROM {table} WHERE {quote_name('cache_key')} IN ({', '.join(['%s'] * len(keys))})",
                    keys,
                )
                return bool(cursor.rowcount)
        except DatabaseError as e:
            logger.warning(f"Database error during delete_many: {e}")
            return False

    def has_key(self, key: str, version: Optional[int] = None) -> bool:
        key = self.make_and_validate_key(key, version)
        db = router.db_for_read(self.cache_model_class)
        connection = connections[db]
        quote_name = connection.ops.quote_name
        now = tz_now().replace(microsecond=0, tzinfo=None)

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"SELECT {quote_name('cache_key')} FROM {quote_name(self._table)} "
                    f"WHERE {quote_name('cache_key')} = %s AND {quote_name('expires')} > %s",
                    [key, connection.ops.adapt_datetimefield_value(now)],
                )
                return cursor.fetchone() is not None
        except DatabaseError as e:
            logger.warning(f"Database error during has_key: {e}")
            return False

    def _cull(self, db: str, cursor, now: datetime, num: int) -> None:
        connection = connections[db]
        table = connection.ops.quote_name(self._table)

        cursor.execute(
            f"DELETE FROM {table} WHERE {connection.ops.quote_name('expires')} < %s",
            [connection.ops.adapt_datetimefield_value(now)],
        )
        deleted_count = cursor.rowcount
        remaining_num = num - deleted_count

        if self._cull_frequency == 0:
            self.clear()
        elif remaining_num > self._max_entries:
            cull_num = remaining_num // self._cull_frequency
            cursor.execute(connection.ops.cache_key_culling_sql() % table, [cull_num])
            last_cache_key = cursor.fetchone()
            if last_cache_key:
                cursor.execute(
                    f"DELETE FROM {table} WHERE                     cursor.execute(
                        f"DELETE FROM {table} WHERE {connection.ops.quote_name('cache_key')} < %s",
                        [last_cache_key[0]],
                    )

    def clear(self) -> None:
        """
        Supprime toutes les entrées de cache dans la table.
        """
        db = router.db_for_write(self.cache_model_class)
        connection = connections[db]
        table = connection.ops.quote_name(self._table)

        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM {table}")
        except DatabaseError as e:
            logger.warning(f"Database error during clear: {e}")
