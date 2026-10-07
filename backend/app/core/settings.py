"""Configuración validada desde variables de entorno y el .env local."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Define secretos y parámetros del backend con validación al arrancar."""
    # Los secretos y parámetros operativos se leen del entorno o del .env local.
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = Field(alias="DATABASE_URL", min_length=1)
    secret_key: SecretStr = Field(alias="SECRET_KEY")
    algorithm: str = "HS256"
    session_inactivity_minutes: int = Field(
        default=3, alias="SESSION_INACTIVITY_MINUTES", gt=0
    )
    session_max_minutes: int = Field(
        default=30, alias="SESSION_MAX_MINUTES", gt=0
    )
    cookie_secure: bool = Field(default=True, alias="COOKIE_SECURE")
    auth_cookie_name: str = "refugio_access_token"
    frontend_url: str = Field(
        default="http://127.0.0.1:5175", alias="FRONTEND_URL"
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, value: SecretStr) -> SecretStr:
        """Exige longitud mínima para el secreto con que se firman los JWT."""
        if len(value.get_secret_value().encode("utf-8")) < 32:
            raise ValueError("SECRET_KEY debe tener al menos 32 bytes")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Rechaza la URL de base de datos que aún contenga una contraseña de ejemplo."""
        value = value.strip()
        if "CAMBIAR_PASSWORD" in value:
            raise ValueError("Actualiza DATABASE_URL con credenciales válidas")
        return value

    @property
    def jwt_secret_key(self) -> str:
        return self.secret_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    """Construye la configuración una sola vez por proceso."""
    return Settings()


settings = get_settings()

DATABASE_URL = settings.database_url
SECRET_KEY = settings.jwt_secret_key
ALGORITHM = settings.algorithm
SESSION_INACTIVITY_MINUTES = settings.session_inactivity_minutes
SESSION_MAX_MINUTES = settings.session_max_minutes
COOKIE_SECURE = settings.cookie_secure
AUTH_COOKIE_NAME = settings.auth_cookie_name
FRONTEND_URL = settings.frontend_url.rstrip("/")
