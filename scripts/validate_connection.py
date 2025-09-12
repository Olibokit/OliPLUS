from load_db_config import load_db_config
from sqlalchemy.exc import OperationalError

def validate_connection():
    engine = load_db_config()
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Connexion réussie :", result.scalar())
    except OperationalError as e:
        print("❌ Échec de connexion :", str(e))

if __name__ == "__main__":
    validate_connection()
