"""Reloj UTC central para fechas operativas y pruebas con tiempo inyectado."""

from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """Devuelve la hora actual con zona UTC."""
    return datetime.now(timezone.utc)
