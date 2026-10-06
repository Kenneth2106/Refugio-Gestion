from sqlalchemy import Boolean, Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(120), nullable=False, unique=True)
    productos = relationship("Producto", back_populates="proveedor")


class Producto(Base):
    # El catálogo es común a las sedes; las existencias viven en Inventario.
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True)
    codigo = Column(String(40), nullable=False, unique=True, index=True)
    nombre = Column(String(120), nullable=False)
    precio_venta = Column(Numeric(12, 2), nullable=False)
    precio_compra = Column(Numeric(12, 2), nullable=False)
    estado = Column(Boolean, nullable=False, default=True)
    proveedor_id = Column(
        Integer,
        ForeignKey("proveedores.id", ondelete="RESTRICT"),
        nullable=False,
    )

    proveedor = relationship("Proveedor", back_populates="productos")
