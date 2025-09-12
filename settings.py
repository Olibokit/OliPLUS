from pydantic import BaseSettings, Field, validator
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str = Field("OliPLUS", description="Nom de l'application cockpit")
    APP_ENV: str = Field("prod", description="Environnement d'exécution (dev, test, prod)")
    APP_DEBUG: bool = Field(False, description="Mode debug activé")
    LOG_DIR: Path = Field("var/log", description="Répertoire des logs cockpit")
    CACHE_DIR: Path = Field("var/cache", description="Répertoire du cache cockpit")
    API_PORT: int = Field(8501, description="Port d'exposition de l'API cockpit")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @validator("APP_ENV")
    def validate_env(cls, v):
        allowed = {"dev", "test", "prod"}
        if v not in allowed:
            raise ValueError(f"APP_ENV doit être l'un de {allowed}")
        return v

    @validator("LOG_DIR", "CACHE_DIR", pre=True)
    def resolve_and_create_path(cls, v):
        path = Path(v).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

settings = Settings()
