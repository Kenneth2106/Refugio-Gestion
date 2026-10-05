from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class UsuarioSede(Base):
    __tablename__ = "usuario_sedes"

    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), primary_key=True)

    usuario = relationship("Usuario", back_populates="sedes")
    sede = relationship("Sede", back_populates="usuarios")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    identificacion = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)

    es_admin = Column(Boolean, default=False, nullable=False)
    es_mesero = Column(Boolean, default=False, nullable=False)
    es_cajero = Column(Boolean, default=False, nullable=False)

    sedes = relationship("UsuarioSede", back_populates="usuario", cascade="all, delete-orphan")