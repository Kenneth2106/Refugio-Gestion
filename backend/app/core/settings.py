import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except ValueError as error:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES debe ser un entero positivo") from error

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").strip().lower() == "true"
AUTH_COOKIE_NAME = "refugio_access_token"

if not DATABASE_URL:
    raise RuntimeError("Configura DATABASE_URL en backend/.env")
if "CAMBIAR_PASSWORD" in DATABASE_URL:
    raise RuntimeError("Actualiza DATABASE_URL con las credenciales de PostgreSQL")
if len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("SECRET_KEY debe tener al menos 32 bytes")
if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError("ACCESS_TOKEN_EXPIRE_MINUTES debe ser un entero positivo")