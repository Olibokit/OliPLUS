#!/usr/bin/env python
# License: GPLv3 Copyright: 2025, Kovid Goyal <kovid at kovidgoyal.net>

import os
import shutil
from contextlib import closing, suppress
from threading import RLock

import apsw

from calibre.prints import debug_print
from calibre.ptempfile import PersistentTemporaryFile, TemporaryDirectory

# 🔒 Lock global pour accès concurrent à la base Kobo
kobo_db_lock = RLock()
INJECT_9P_ERROR = False


def row_factory(cursor: apsw.Cursor, row: tuple) -> dict:
    """
    Convertit une ligne SQLite en dictionnaire clé/valeur.
    """
    return {k[0]: row[i] for i, k in enumerate(cursor.getdescription())}


def wal_path(path: str) -> str:
    """
    Retourne le chemin du fichier WAL associé à une base SQLite.
    """
    return path + '-wal'


def copy_db(conn: apsw.Connection, dest_path: str) -> None:
    """
    Copie la base SQLite en vidant le WAL et en sauvegardant dans un fichier temporaire.
    """
    with suppress(AttributeError):
        conn.cache_flush()
    conn.wal_checkpoint(mode=apsw.SQLITE_CHECKPOINT_TRUNCATE)

    with TemporaryDirectory() as tdir:
        tempdb = os.path.join(tdir, 'temp.sqlite')
        with closing(apsw.Connection(tempdb)) as dest, dest.backup('main', conn, 'main') as b:
            while not b.done:
                with suppress(apsw.BusyError, apsw.LockedError):
                    b.step()
        shutil.move(tempdb, dest_path)

        twal, dwal = wal_path(tempdb), wal_path(dest_path)
        if os.path.exists(twal):
            shutil.move(twal, dwal)
        else:
            with suppress(FileNotFoundError):
                os.remove(dwal)


class Database:
    """
    Gère la connexion à une base SQLite Kobo avec verrouillage et copie temporaire.
    """

    def __init__(self, path_on_device: str):
        self.path_on_device = self.dbpath = path_on_device
        self.dbversion = 0
        self.needs_copy = True
        self.use_row_factory = True

        with kobo_db_lock:
            try:
                self._connect(path_on_device)
                self.needs_copy = False
            except apsw.IOError:
                debug_print(f'Kobo: I/O error connecting to {self.path_on_device}, copying to temp storage')
                with open(self.path_on_device, 'rb') as src, PersistentTemporaryFile(suffix='-kobo-db.sqlite') as dest:
                    shutil.copyfileobj(src, dest)
                wal = wal_path(self.path_on_device)
                if os.path.exists(wal):
                    shutil.copy2(wal, wal_path(dest.name))
                try:
                    self._connect(dest.name)
                except Exception:
                    os.remove(dest.name)
                    raise

    def _connect(self, path: str) -> None:
        """
        Connecte à la base SQLite et lit la version.
        """
        if INJECT_9P_ERROR:
            raise apsw.IOError('Fake I/O error to test 9p codepath')
        with closing(apsw.Connection(path)) as conn:
            conn.setrowtrace(row_factory)
            cursor = conn.cursor()
            cursor.execute('SELECT version FROM dbversion')
            with suppress(StopIteration):
                result = next(cursor)
                self.dbversion = result['version']
            debug_print('Kobo database version:', self.dbversion)
            self.dbpath = path

    def __enter__(self) -> apsw.Connection:
        """
        Active le contexte de connexion à la base.
        """
        kobo_db_lock.acquire()
        self.conn = apsw.Connection(self.dbpath)
        if self.use_row_factory:
            self.conn.setrowtrace(row_factory)
        return self.conn.__enter__()

    def __exit__(self, exc_type, exc_value, tb) -> bool | None:
        """
        Ferme la connexion et copie la base si nécessaire.
        """
        try:
            with closing(self.conn):
                suppress_exception = self.conn.__exit__(exc_type, exc_value, tb)
                if self.needs_copy and (
                    suppress_exception or (exc_type is None and exc_value is None and tb is None)
                ):
                    copy_db(self.conn, self.path_on_device)
        finally:
            kobo_db_lock.release()
        return suppress_exception
