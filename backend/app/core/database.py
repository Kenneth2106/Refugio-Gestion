"""Motor SQLAlchemy, fábrica de sesiones y dependencia de base de datos."""

from collections.abc import Generator
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.settings import DATABASE_URL


if environ.get("VERCEL") == "1":
    engine = create_engine(DATABASE_URL, poolclass=NullPool, pool_pre_ping=True)
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# Los modelos comparten este registro y los endpoints reciben sesiones independientes.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# FastAPI reutiliza esta dependencia y cierra la sesión al terminar cada petición.
def get_db() -> Generator:
    """Entrega una sesión por petición y garantiza su cierre."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
