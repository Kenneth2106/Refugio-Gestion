"""Eventos de auditoría asociados a las operaciones relevantes del negocio."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.core.database import Base


class EventoAuditoria(Base):
    """Registra quién realizó una operación y su contexto, sin datos sensibles."""

    __tablename__ = "eventos_auditoria"

    id = Column(Integer, primary_key=True)
    actor_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
    )
    sede_id = Column(
        Integer,
        ForeignKey("sedes.id", ondelete="SET NULL"),
        nullable=True,
    )
    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id", ondelete="SET NULL"),
        nullable=True,
    )
    accion = Column(String(40), nullable=False)
    creado_en = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
