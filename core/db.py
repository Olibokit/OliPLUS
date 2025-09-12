from sqlalchemy.orm import sessionmaker
from config.load_db_config import load_db_config

engine = load_db_config()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
