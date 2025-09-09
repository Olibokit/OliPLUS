import logging
from typing import Optional
from olibokit.models import User
from olibokit.database import db

logger = logging.getLogger("admin_context")

class AdminUserNotFound(Exception):
    """Exception levée si l'utilisateur admin est introuvable."""
    pass

def get_admin_user() -> User:
    """
    Récupère l'utilisateur admin depuis la base cockpit.

    Returns:
        User: instance de l'utilisateur admin

    Raises:
        AdminUserNotFound: si aucun utilisateur admin n'est trouvé
    """
    try:
        admin: Optional[User] = db.query(User).filter_by(username="admin").first()
        if not admin:
            logger.error("❌ Utilisateur admin introuvable dans la base cockpit")
            raise AdminUserNotFound("Admin user not found")
        
        logger.info(f"✅ Utilisateur admin récupéré : {admin.username}")
        return admin

    except Exception as e:
        logger.exception("🚨 Erreur lors de la récupération de l'utilisateur admin")
        raise
