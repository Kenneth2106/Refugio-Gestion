"""Modelos ORM de sedes y mesas físicas."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Sede(Base):
    """Sede operativa que reúne mesas, asignaciones y existencias."""
    __tablename__ = "sedes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    direccion = Column(String(200), nullable=False, default="Por definir", server_default="Por definir")
    estado = Column(Boolean, default=True, nullable=False)

    mesas = relationship("Mesa", back_populates="sede", cascade="all, delete-orphan")
    usuarios = relationship("UsuarioSede", back_populates="sede", cascade="all, delete-orphan")


class Mesa(Base):
    """Mesa numerada por sede; su estado operativo deriva de pedidos abiertos."""
    __tablename__ = "mesas"
    __table_args__ = (UniqueConstraint("sede_id", "numero", name="uq_mesas_sede_numero"),)

    id = Column(Integer, primary_key=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False)
    numero = Column(Integer, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)

    sede = relationship("Sede", back_populates="mesas")
