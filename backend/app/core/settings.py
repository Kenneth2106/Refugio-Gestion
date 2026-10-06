import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
SECRET_KEY = os.getenv("SECRET_KEY", "")
ALGORITHM = "HS256"

try:
    SESSION_INACTIVITY_MINUTES = int(os.getenv("SESSION_INACTIVITY_MINUTES", "3"))
    SESSION_MAX_MINUTES = int(os.getenv("SESSION_MAX_MINUTES", "30"))
except ValueError as error:
    raise RuntimeError("Tiempos de sesión deben ser enteros positivos") from error

COOKIE_SECURE = os.getenv("COOKIE_SECURE", "true").strip().lower() == "true"
AUTH_COOKIE_NAME = "refugio_access_token"
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5175").rstrip("/")

if not DATABASE_URL:
    raise RuntimeError("Configura DATABASE_URL en backend/.env")
if "CAMBIAR_PASSWORD" in DATABASE_URL:
    raise RuntimeError("Actualiza DATABASE_URL con las credenciales de PostgreSQL")
if len(SECRET_KEY.encode("utf-8")) < 32:
    raise RuntimeError("SECRET_KEY debe tener al menos 32 bytes")
if SESSION_INACTIVITY_MINUTES <= 0 or SESSION_MAX_MINUTES <= 0:
    raise RuntimeError("Los tiempos de sesión deben ser enteros positivos")