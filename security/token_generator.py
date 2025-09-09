import jwt
from datetime import datetime, timedelta
from typing import Optional
from your_app.models import User
from your_app.database import get_user_by_id

SECRET_KEY = "your-secret-key"  # 🔐 à stocker dans .env
ALGORITHM = "HS256"
EXPIRATION_MINUTES = 30

def generate_reset_token(user: User) -> str:
    payload = {
        "sub": str(user.id),
        "exp": datetime.utcnow() + timedelta(minutes=EXPIRATION_MINUTES),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_reset_token(token: str) -> Optional[User]:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(decoded.get("sub"))
        return get_user_by_id(user_id)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None
