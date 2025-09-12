import os
import time
import threading
import logging
from werkzeug import urls
import psycopg2
import psycopg2.extensions
from psycopg2.pool import PoolError

import odoo
from .cursor import Cursor  # Assure-toi que Cursor est bien défini dans cursor.py
from . import tools

_logger = logging.getLogger(__name__)
_logger_conn = _logger.getChild("connection")

MAX_IDLE_TIMEOUT = 600  # 10 minutes

class ConnectionPool:
    def __init__(self, maxconn: int = 64, readonly: bool = False):
        self._connections = []
        self._maxconn = max(1, maxconn)
        self._readonly = readonly
        self._lock = threading.Lock()

    def __repr__(self):
        used = sum(1 for c, u, _ in self._connections if u)
        total = len(self._connections)
        mode = 'read-only' if self._readonly else 'read/write'
        return f"ConnectionPool({mode};used={used}/total={total}/max={self._maxconn})"

    @property
    def readonly(self):
        return self._readonly

    def _debug(self, msg, *args):
        _logger_conn.debug(('%r ' + msg), self, *args)

    @tools.locked
    def borrow(self, connection_info: dict) -> psycopg2.extensions.connection:
        for i, (cnx, used, last_used) in tools.reverse_enumerate(self._connections):
            if not used and not cnx.closed and time.time() - last_used > MAX_IDLE_TIMEOUT:
                self._debug('Closing idle connection at index %d: %r', i, cnx.dsn)
                cnx.close()
            if cnx.closed:
                self._connections.pop(i)
                self._debug('Removing closed connection at index %d: %r', i, cnx.dsn)
                continue
            if getattr(cnx, 'leaked', False):
                delattr(cnx, 'leaked')
                self._connections[i][1] = False
                _logger.info('%r: Recovered leaked connection to %r', self, cnx.dsn)

        for i, (cnx, used, _) in enumerate(self._connections):
            if not used and self._dsn_equals(cnx.dsn, connection_info):
                try:
                    cnx.reset()
                except psycopg2.OperationalError:
                    self._debug('Reset failed at index %d: %r', i, cnx.dsn)
                    if not cnx.closed:
                        cnx.close()
                    continue
                self._connections[i][1] = True
                self._debug('Borrowed existing connection to %r at index %d', cnx.dsn, i)
                return cnx

        if len(self._connections) >= self._maxconn:
            for i, (cnx, used, _) in enumerate(self._connections):
                if not used:
                    self._connections.pop(i)
                    if not cnx.closed:
                        cnx.close()
                    self._debug('Removed old connection at index %d: %r', i, cnx.dsn)
                    break
            else:
                raise PoolError('Connection pool is full')

        try:
            result = psycopg2.connect(connection_factory=PsycoConnection, **connection_info)
        except psycopg2.Error:
            _logger.info('Connection to database failed')
            raise

        self._connections.append([result, True, 0])
        self._debug('Created new connection backend PID %d', result.get_backend_pid())
        return result

    @tools.locked
    def give_back(self, connection, keep_in_pool=True):
        self._debug('Returning connection to %r', connection.dsn)
        for i, (cnx, _, _) in enumerate(self._connections):
            if cnx is connection:
                if keep_in_pool:
                    self._connections[i][1] = False
                    self._connections[i][2] = time.time()
                    self._debug('Connection returned to pool: %r', cnx.dsn)
                else:
                    self._connections.pop(i)
                    self._debug('Connection removed from pool: %r', cnx.dsn)
                    cnx.close()
                return
        raise PoolError('Connection does not belong to pool')

    @tools.locked
    def close_all(self, dsn=None):
        count = 0
        last = None
        for i, (cnx, _, _) in tools.reverse_enumerate(self._connections):
            if dsn is None or self._dsn_equals(cnx.dsn, dsn):
                cnx.close()
                last = self._connections.pop(i)[0]
                count += 1
        if count:
            _logger.info('%r: Closed %d connections %s', self, count,
                         (dsn and last and f'to {last.dsn}') or '')

    def _dsn_equals(self, dsn1, dsn2):
        alias_keys = {'dbname': 'database'}
        ignore_keys = ['password']
        dsn1, dsn2 = ({
            alias_keys.get(k, k): str(v)
            for k, v in (psycopg2.extensions.parse_dsn(dsn) if isinstance(dsn, str) else dsn).items()
            if k not in ignore_keys
        } for dsn in (dsn1, dsn2))
        return dsn1 == dsn2


class PsycoConnection(psycopg2.extensions.connection):
    def lobject(*args, **kwargs):
        pass

    if hasattr(psycopg2.extensions, 'ConnectionInfo'):
        @property
        def info(self):
            class Info(psycopg2.extensions.ConnectionInfo):
                @property
                def password(self):
                    pass
            return Info(self)


class Connection:
    def __init__(self, pool: ConnectionPool, dbname: str, dsn: dict):
        self.__pool = pool
        self.__dbname = dbname
        self.__dsn = dsn

    @property
    def dsn(self):
        dsn = dict(self.__dsn)
        dsn.pop('password', None)
        return dsn

    @property
    def dbname(self):
        return self.__dbname

    def cursor(self):
        _logger.debug('Creating cursor for %r', self.dsn)
        return Cursor(self.__pool, self.__dbname, self.__dsn)

    def __bool__(self):
        raise NotImplementedError()


def connection_info_for(db_or_uri: str, readonly: bool = False) -> tuple[str, dict]:
    if 'ODOO_PGAPPNAME' in os.environ:
        app_name = os.environ['ODOO_PGAPPNAME'].replace('{pid}', str(os.getpid()))[:63]
    else:
        app_name = f"odoo-{os.getpid()}"

    if db_or_uri.startswith(('postgresql://', 'postgres://')):
        us = urls.url_parse(db_or_uri)
        db_name = us.path[1:] if len(us.path) > 1 else us.username or us.hostname
        return db_name, {'dsn': db_or_uri, 'application_name': app_name}

    connection_info = {'database': db_or_uri, 'application_name': app_name}
    for p in ('host', 'port', 'user', 'password', 'sslmode'):
        cfg = tools.config['db_' + p]
        if readonly:
            cfg = tools.config.get('db_replica_' + p, cfg)
        if cfg:
            connection_info[p] = cfg

    return db_or_uri, connection_info


_Pool = None
_Pool_readonly = None

def db_connect(to: str, allow_uri: bool = False, readonly: bool = False) -> Connection:
    global _Pool, _Pool_readonly

    maxconn = tools.config['db_maxconn_gevent'] if odoo.evented else tools.config['db_maxconn']
    if _Pool is None and not readonly:
        _Pool = ConnectionPool(int(maxconn), readonly=False)
    if _Pool_readonly is None and readonly:
        _Pool_readonly = ConnectionPool(int(maxconn), readonly=True)

   db, info = connection_info_for(to, readonly)
   
    if not allow_uri and db != to:
        raise ValueError("URI connections are not allowed")

    pool = _Pool_readonly if readonly else _Pool
    return Connection(pool, db, info)


def close_db(db_name: str):
    """Close all connections related to a specific database name."""
    if _Pool:
        _Pool.close_all(connection_info_for(db_name)[1])
    if _Pool_readonly:
        _Pool_readonly.close_all(connection_info_for(db_name, readonly=True)[1])


def close_all():
    """Close all connections in all pools."""
    if _Pool:
        _Pool.close_all()
    if _Pool_readonly:
        _Pool_readonly.close_all()
