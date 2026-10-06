from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, Integer, String

from app.core.database import Base


class SesionActiva(Base):
    __tablename__ = "sesiones_activas"
    __table_args__ = (
        Index("ix_sesiones_activas_usuario_activa", "usuario_id", "activa"),
    )

    id = Column(Integer, primary_key=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    jti = Column(String(128), unique=True, nullable=False)
    creada_en = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    ultima_actividad = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    activa = Column(Boolean, default=True, nullable=False)
    revocada_en = Column(DateTime(timezone=True), nullable=True)
    sede_seleccionada_id = Column(
        Integer,
        ForeignKey("sedes.id", ondelete="SET NULL"),
        nullable=True,
    )