from odoo.exceptions import AccessDenied
from db_admin_operations import (
    exp_db_exist,
    exp_list,
    exp_list_lang,
    exp_server_version,
    exp_migrate_databases,
    exp_list_countries,
    list_db_incompatible
)

def check_super(password: str):
    # Implémentation à adapter selon ton système de sécurité
    if password != "your_super_password":
        raise AccessDenied("Invalid super password")


def dispatch(method: str, params: list) -> any:
    exposed_methods = {
        'db_exist': exp_db_exist,
        'list': exp_list,
        'list_lang': exp_list_lang,
        'server_version': exp_server_version,
        'migrate_databases': exp_migrate_databases,
        'list_countries': exp_list_countries,
        'list_db_incompatible': list_db_incompatible,
    }

    if method in ['db_exist', 'list', 'list_lang', 'server_version']:
        return exposed_methods[method](*params)

    elif method in exposed_methods:
        password = params[0]
        args = params[1:]
        check_super(password)
        return exposed_methods[method](*args)

    else:
        raise KeyError(f"Method not found: {method}")
