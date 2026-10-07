"""Motor SQLAlchemy, fábrica de sesiones y dependencia de base de datos."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.settings import DATABASE_URL


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
