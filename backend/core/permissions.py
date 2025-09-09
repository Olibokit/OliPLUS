# 🔐 modules/permissions.py — Gestion des permissions cockpit

AUTHORIZED_USERS = {
    "olivier": ["upload", "read"],
    "admin": ["upload", "read", "delete"],
    "invite": ["read"]
}


def has_permission_to_upload(user: str, metadata: dict) -> bool:
    """
    Vérifie si l'utilisateur a le droit d'uploader un document.
    """
    return "upload" in AUTHORIZED_USERS.get(user, [])


def has_permission_to_read(user: str) -> bool:
    """
    Vérifie si l'utilisateur peut lire les documents archivés.
    """
    return "read" in AUTHORIZED_USERS.get(user, [])


def has_permission_to_delete(user: str) -> bool:
    """
    Vérifie si l'utilisateur peut supprimer un document.
    """
    return "delete" in AUTHORIZED_USERS.get(user, [])
