import base64
import hmac
import hashlib
import time
from typing import Optional
from pydantic import BaseModel

from olibokit.dependencies import get_user_by_id  # À adapter à ta source utilisateur

SECRET_KEY = b"cockpit-reset-secret-2025"
TOKEN_EXPIRATION_SECONDS = 900  # 15 minutes

class User(BaseModel):
    id: str
    email: str


def generate_reset_token(user: User) -> str:
    """
    🎟️ Génère un token sécurisé pour réinitialisation.

    Format : base64(user_id + expiration + signature)

    :param user: Utilisateur cible
    :return: Token sécurisé en base64
    """
    expires = int(time.time()) + TOKEN_EXPIRATION_SECONDS
    data = f"{user.id}:{expires}".encode()
    signature = hmac.new(SECRET_KEY, data, hashlib.sha256).hexdigest()
    token_raw = f"{user.id}:{expires}:{signature}"
    return base64.urlsafe_b64encode(token_raw.encode()).decode()


def verify_reset_token(token: str) -> Optional[User]:
    """
    ✅ Vérifie un token de réinitialisation sécurisé.

    :param token: Token reçu
    :return: Utilisateur si token valide, sinon None
    """
    try:
        decoded = base64.urlsafe_b64decode(token).decode()
        user_id, expires_str, signature = decoded.split(":")

        expires = int(expires_str)
        if time.time() > expires:
            return None  # ⏳ Expiré

        expected_signature = hmac.new(
            SECRET_KEY, f"{user_id}:{expires}".encode(), hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(expected_signature, signature):
            return None  # ❌ Signature invalide

        return get_user_by_id(user_id)  # 🎯 Récupère l’utilisateur
    except Exception:
        return None
