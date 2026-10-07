"""Modelos de pedidos abiertos y líneas con precios históricos."""

from datetime import datetime, timezone

from sqlalchemy import (
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    column,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Pedido(Base):
    """Pedido asociado a usuario, sede y mesa, con unicidad si está abierto."""
    __tablename__ = "pedidos"
    __table_args__ = (
        # PostgreSQL permite solo un pedido ABIERTO por mesa, incluso con concurrencia.
        Index(
            "uq_pedidos_mesa_abierto",
            "mesa_id",
            unique=True,
            postgresql_where=column("estado") == "ABIERTO",
        ),
    )

    id = Column(Integer, primary_key=True)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    sede_id = Column(
        Integer,
        ForeignKey("sedes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    mesa_id = Column(
        Integer,
        ForeignKey("mesas.id", ondelete="RESTRICT"),
        nullable=False,
    )
    estado = Column(String(20), nullable=False, default="ABIERTO")
    creado_en = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    lineas = relationship(
        "LineaPedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
        order_by="LineaPedido.id",
    )


class LineaPedido(Base):
    """Producto/cantidad del pedido con precio, usuario y fecha de registro."""
    __tablename__ = "lineas_pedido"
    __table_args__ = (
        CheckConstraint("cantidad > 0", name="ck_linea_pedido_cantidad_positiva"),
        CheckConstraint("precio_unitario >= 0", name="ck_linea_pedido_precio_no_negativo"),
    )

    id = Column(Integer, primary_key=True)
    pedido_id = Column(
        Integer,
        ForeignKey("pedidos.id", ondelete="RESTRICT"),
        nullable=False,
    )
    producto_id = Column(
        Integer,
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(12, 2), nullable=False)
    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=False,
    )
    creado_en = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    pedido = relationship("Pedido", back_populates="lineas")
    producto = relationship("Producto")
