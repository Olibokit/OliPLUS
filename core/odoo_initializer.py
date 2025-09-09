import logging
from enum import IntEnum
from psycopg2.extras import Json
import odoo.modules

_logger = logging.getLogger(__name__)


def is_initialized(cr) -> bool:
    """Check if the database is initialized for the ORM."""
    return odoo.tools.sql.table_exists(cr, 'ir_module_module')


def initialize(cr):
    """Initialize the database for Odoo ORM with base modules and categories."""
    try:
        f = odoo.tools.misc.file_path('base/data/base_data.sql')
    except FileNotFoundError:
        msg = "File not found: 'base.sql' (required by module 'base')."
        _logger.critical(msg)
        raise IOError(msg)

    with odoo.tools.misc.file_open(f) as base_sql_file:
        cr.execute(base_sql_file.read())  # ⚠️ raw SQL execution

    for module_name in odoo.modules.get_modules():
        mod_path = odoo.modules.get_module_path(module_name)
        if not mod_path:
            continue

        info = odoo.modules.get_manifest(module_name)
        if not info:
            continue

        categories = info['category'].split('/')
        category_id = create_categories(cr, categories)

        state = 'uninstalled' if info['installable'] else 'uninstallable'

        cr.execute("""
            INSERT INTO ir_module_module (
                author, website, name, shortdesc, description,
                category_id, auto_install, state, web, license,
                application, icon, sequence, summary
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            info['author'], info['website'], module_name,
            Json({'en_US': info['name']}), Json({'en_US': info['description']}),
            category_id, info.get('auto_install', True), state,
            info['web'], info['license'], info['application'],
            info['icon'], info['sequence'], Json({'en_US': info['summary']})
        ))
        module_id = cr.fetchone()[0]

        cr.execute("""
            INSERT INTO ir_model_data (name, model, module, res_id, noupdate)
            VALUES (%s, %s, %s, %s, %s)
        """, (f'module_{module_name}', 'ir.module.module', 'base', module_id, True))

        for dep in info['depends']:
            cr.execute("""
                INSERT INTO ir_module_module_dependency (module_id, name, auto_install_required)
                VALUES (%s, %s, %s)
            """, (module_id, dep, dep in (info.get('auto_install') or [])))

    _auto_install_modules(cr)


def _auto_install_modules(cr):
    """Recursively mark auto-installable modules for installation."""
    while True:
        cr.execute("""
            SELECT m.name FROM ir_module_module m
            WHERE m.auto_install
              AND state NOT IN ('to install', 'uninstallable')
              AND NOT EXISTS (
                  SELECT 1 FROM ir_module_module_dependency d
                  JOIN ir_module_module mdep ON d.name = mdep.name
                  WHERE d.module_id = m.id
                    AND d.auto_install_required
                    AND mdep.state != 'to install'
              )
        """)
        to_install = [row[0] for row in cr.fetchall()]

        cr.execute("""
            SELECT d.name FROM ir_module_module_dependency d
            JOIN ir_module_module m ON d.module_id = m.id
            JOIN ir_module_module mdep ON d.name = mdep.name
            WHERE (m.state = 'to install' OR m.name = ANY(%s))
              AND NOT (mdep.state = 'to install' OR mdep.name = ANY(%s))
        """, [to_install, to_install])
        to_install += [row[0] for row in cr.fetchall()]

        if not to_install:
            break

        cr.execute("UPDATE ir_module_module SET state='to install' WHERE name IN %s", (tuple(to_install),))


def create_categories(cr, categories: list[str]) -> int:
    """Create nested ir_module_category entries and return the last category ID."""
    parent_id = None
    path = []

    for name in categories:
        path.append(name)
        xml_id = 'module_category_' + '_'.join(x.lower().replace('&', 'and').replace(' ', '_') for x in path)

        cr.execute("""
            SELECT res_id FROM ir_model_data
            WHERE name=%s AND module='base' AND model='ir.module.category'
        """, (xml_id,))
        result = cr.fetchone()

        if result:
            category_id = result[0]
        else:
            cr.execute("""
                INSERT INTO ir_module_category (name, parent_id)
                VALUES (%s, %s) RETURNING id
            """, (Json({'en_US': name}), parent_id))
            category_id = cr.fetchone()[0]

            cr.execute("""
                INSERT INTO ir_model_data (module, name, res_id, model, noupdate)
                VALUES ('base', %s, %s, 'ir.module.category', TRUE)
            """, (xml_id, category_id))

        parent_id = category_id

    return parent_id


class FunctionStatus(IntEnum):
    MISSING = 0
    PRESENT = 1
    INDEXABLE = 2


def has_unaccent(cr) -> FunctionStatus:
    """Check if 'unaccent' function exists and is indexable (immutable)."""
    cr.execute("""
        SELECT p.provolatile
        FROM pg_proc p
        LEFT JOIN pg_namespace ns ON p.pronamespace = ns.oid
        WHERE p.proname = 'unaccent'
          AND p.pronargs = 1
          AND ns.nspname = 'public'
    """)
    result = cr.fetchone()
    if not result:
        return FunctionStatus.MISSING
    return FunctionStatus.INDEXABLE if result[0] == 'i' else FunctionStatus.PRESENT


def has_trigram(cr) -> bool:
    """Check if 'word_similarity' function from pg_trgm is available."""
    cr.execute("SELECT proname FROM pg_proc WHERE proname='word_similarity'")
    return bool(cr.fetchall())
