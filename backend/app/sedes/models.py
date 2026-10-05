from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Sede(Base):
    __tablename__ = "sedes"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)

    mesas = relationship("Mesa", back_populates="sede", cascade="all, delete-orphan")
    usuarios = relationship("UsuarioSede", back_populates="sede", cascade="all, delete-orphan")


class Mesa(Base):
    __tablename__ = "mesas"

    id = Column(Integer, primary_key=True, index=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), nullable=False)
    numero = Column(Integer, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)

    sede = relationship("Sede", back_populates="mesas")
