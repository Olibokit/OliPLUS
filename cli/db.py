import argparse
import io
import sys
import zipfile
import urllib.parse
from functools import partial
from pathlib import Path
from typing import Union

import requests

from . import Command
from .server import report_configuration
from ..service.db import (
    dump_db, exp_drop, exp_db_exist,
    exp_duplicate_database, exp_rename, restore_db
)
from ..tools import config

eprint = partial(print, file=sys.stderr, flush=True)


class Db(Command):
    """🔧 CLI tool to manage Odoo databases with filestore support."""
    name = 'db'

    def run(self, cmdargs: list[str]) -> None:
        parser = argparse.ArgumentParser(
            prog=f'{Path(sys.argv[0]).name} {self.name}',
            description=self.__doc__.strip()
        )
        self._add_common_args(parser)
        subs = parser.add_subparsers()

        self._add_load_parser(subs)
        self._add_dump_parser(subs)
        self._add_duplicate_parser(subs)
        self._add_rename_parser(subs)
        self._add_drop_parser(subs)

        args = parser.parse_args(cmdargs)
        self._configure_odoo(args)
        args.func(args)

    def _add_common_args(self, parser):
        parser.add_argument('-c', '--config')
        parser.add_argument('-D', '--data-dir')
        parser.add_argument('--addons-path')
        parser.add_argument('-r', '--db_user')
        parser.add_argument('-w', '--db_password')
        parser.add_argument('--pg_path')
        parser.add_argument('--db_host')
        parser.add_argument('--db_port')
        parser.add_argument('--db_sslmode')
        parser.set_defaults(func=lambda _: exit(parser.format_help()))

    def _configure_odoo(self, args):
        config.parse_config([
            val
            for k, v in vars(args).items()
            if v is not None and (k in ['config', 'data_dir', 'addons_path'] or k.startswith(('db_', 'pg_')))
            for val in [
                '--data-dir' if k == 'data_dir' else '--addons-path' if k == 'addons_path' else f'--{k}',
                v,
            ]
        ], setup_logging=True)
        config['list_db'] = True
        report_configuration()

    def _add_load_parser(self, subs):
        load = subs.add_parser("load", help="Load a zipped dump file (with filestore).")
        load.set_defaults(func=self.load)
        load.add_argument('-f', '--force', action='store_true', help="Drop target DB if it exists")
        load.add_argument('-n', '--neutralize', action='store_true', help="Neutralize DB after restore")
        load.add_argument('database', nargs='?', help="Target DB name (defaults to dump filename)")
        load.add_argument('dump_file', help="Path or URL to zipped dump file")

    def _add_dump_parser(self, subs):
        dump = subs.add_parser("dump", help="Create a zipped dump with filestore.")
        dump.set_defaults(func=self.dump)
        dump.add_argument('database', help="Database to dump")
        dump.add_argument('dump_path', nargs='?', default='-', help="Path to save dump (or '-' for stdout)")

    def _add_duplicate_parser(self, subs):
        duplicate = subs.add_parser("duplicate", help="Duplicate a DB with filestore.")
        duplicate.set_defaults(func=self.duplicate)
        duplicate.add_argument('-f', '--force', action='store_true', help="Drop target DB if it exists")
        duplicate.add_argument('-n', '--neutralize', action='store_true', help="Neutralize target DB")
        duplicate.add_argument('source')
        duplicate.add_argument('target')

    def _add_rename_parser(self, subs):
        rename = subs.add_parser("rename", help="Rename a DB with filestore.")
        rename.set_defaults(func=self.rename)
        rename.add_argument('-f', '--force', action='store_true', help="Drop target DB if it exists")
        rename.add_argument('source')
        rename.add_argument('target')

    def _add_drop_parser(self, subs):
        drop = subs.add_parser("drop", help="Drop a DB and its filestore.")
        drop.set_defaults(func=self.drop)
        drop.add_argument('database')

    def load(self, args):
        db_name = args.database or Path(args.dump_file).stem
        self._check_target(db_name, delete_if_exists=args.force)

        dump_file: Union[str, io.BytesIO]
        url = urllib.parse.urlparse(args.dump_file)
        if url.scheme:
            eprint(f"Fetching {args.dump_file}...", end='')
            r = requests.get(args.dump_file, timeout=10)
            if not r.ok:
                exit(f"❌ Unable to fetch {args.dump_file}: {r.reason}")
            eprint(" done")
            dump_file = io.BytesIO(r.content)
        else:
            eprint(f"Restoring {args.dump_file}...")
            dump_file = args.dump_file

        if not zipfile.is_zipfile(dump_file):
            exit("❌ Not a zipped dump file. Use `pg_restore` or `psql` for raw formats.")

        restore_db(db=db_name, dump_file=dump_file, copy=True, neutralize_database=args.neutralize)

    def dump(self, args):
        if args.dump_path == '-':
            dump_db(args.database, sys.stdout.buffer)
        else:
            with open(args.dump_path, 'wb') as f:
                dump_db(args.database, f)

    def duplicate(self, args):
        self._check_target(args.target, delete_if_exists=args.force)
        exp_duplicate_database(args.source, args.target, neutralize_database=args.neutralize)

    def rename(self, args):
        self._check_target(args.target, delete_if_exists=args.force)
        exp_rename(args.source, args.target)

    def drop(self, args):
        if not exp_drop(args.database):
            exit(f"❌ Database {args.database} does not exist.")

    def _check_target(self, target: str, delete_if_exists: bool):
        if exp_db_exist(target):
            if delete_if_exists:
                exp_drop(target)
            else:
                exit(f"❌ Target DB '{target}' exists.\nUse `--force` to overwrite.")
