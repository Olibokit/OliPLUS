import logging
from typing import Optional
from datetime import datetime, timedelta

from passlib.context import CryptContext
from your_app.models import User  # Remplace par ton modèle réel
from your_app.tokens import verify_reset_token, generate_reset_token
from your_app.email import send_password_reset_email
from your_app.database import get_user_by_username, get_user_by_email, update_user_password

logger = logging.getLogger("cockpit.auth")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 🔐 Authentifie un utilisateur avec mot de passe
def authenticate_user(username: str, password: str) -> Optional[User]:
    user = get_user_by_username(username)
    if not user:
        logger.warning(f"🔐 Utilisateur introuvable : {username}")
        return None
    if not pwd_context.verify(password, user.hashed_password):
        logger.warning(f"🔐 Mot de passe incorrect pour : {username}")
        return None
    logger.info(f"✅ Authentification réussie pour : {username}")
    return user

# 🔁 Réinitialise le mot de passe via un token sécurisé
def reset_password_with_token(token: str, new_password: str) -> bool:
    user = verify_reset_token(token)
    if not user:
        logger.warning("⚠️ Token de réinitialisation invalide ou expiré.")
        return False
    hashed = pwd_context.hash(new_password)
    update_user_password(user.id, hashed)
    logger.info(f"🔁 Mot de passe réinitialisé pour : {user.username}")
    return True

# 📩 Envoie un email de réinitialisation avec token
def request_password_reset(email: str) -> bool:
    user = get_user_by_email(email)
    if not user:
        logger.warning(f"📭 Aucun utilisateur avec l’email : {email}")
        return False
    token = generate_reset_token(user)
    send_password_reset_email(user.email, token)
    logger.info(f"📨 Email de réinitialisation envoyé à : {email}")
    return True
