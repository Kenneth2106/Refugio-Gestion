"""Modelos ORM de usuarios, roles y relaciones usuario-sede."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class UsuarioSede(Base):
    """Tabla de asociación muchos-a-muchos entre usuarios operativos y sedes."""
    __tablename__ = "usuario_sedes"

    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True)
    sede_id = Column(Integer, ForeignKey("sedes.id", ondelete="CASCADE"), primary_key=True)

    usuario = relationship("Usuario", back_populates="sedes")
    sede = relationship("Sede", back_populates="usuarios")


class Usuario(Base):
    """Cuenta autenticable con hash bcrypt, estado y capacidades de rol."""
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    identificacion = Column(String, unique=True, nullable=False, index=True)
    nombre = Column(String, nullable=False)
    nombre_usuario = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    hashed_password = Column(String, nullable=False)
    estado = Column(Boolean, default=True, nullable=False)

    es_admin = Column(Boolean, default=False, nullable=False)
    es_mesero = Column(Boolean, default=False, nullable=False)
    es_cajero = Column(Boolean, default=False, nullable=False)

    sedes = relationship("UsuarioSede", back_populates="usuario", cascade="all, delete-orphan")