from your_app.models import User
from your_app.orm import SessionLocal

def get_user_by_id(user_id: int) -> Optional[User]:
    with SessionLocal() as db:
        return db.query(User).filter(User.id == user_id).first()

def update_user_password(user_id: int, hashed_password: str) -> None:
    with SessionLocal() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            user.hashed_password = hashed_password
            db.commit()
