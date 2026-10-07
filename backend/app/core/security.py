"""Operaciones criptográficas para contraseñas bcrypt y tokens JWT."""

from datetime import datetime, timedelta, timezone
from typing import Mapping

import bcrypt
from jose import jwt
from app.core.settings import SESSION_MAX_MINUTES, ALGORITHM, SECRET_KEY


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara una contraseña ingresada con el hash persistido."""
    # bcrypt compara la clave con el hash persistido, nunca con texto plano.
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("ascii"),
        )
    except (TypeError, ValueError):
        return False


def get_password_hash(password: str) -> str:
    """Genera un hash bcrypt; rechaza valores que exceden el límite de 72 bytes."""
    # bcrypt limita la entrada a 72 bytes; se valida antes de generar el hash.
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("La contraseña supera el máximo permitido por bcrypt")
    return bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode("ascii")


def create_access_token(
    data: Mapping[str, object],
    expires_delta: timedelta | None = None,
    issued_at: datetime | None = None,
) -> str:
    """Firma un JWT con instante de emisión y expiración en UTC."""
    # El JWT identifica la sesión, cuyo jti y vigencia se verifican también en la base.
    to_encode = data.copy()
    now = issued_at or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    else:
        now = now.astimezone(timezone.utc)
    to_encode.update(
        {
            "iat": now,
            "exp": now
            + (expires_delta or timedelta(minutes=SESSION_MAX_MINUTES)),
        }
    )
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, object]:
    """Verifica y decodifica la firma y expiración del JWT."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])