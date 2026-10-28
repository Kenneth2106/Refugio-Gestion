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
        Index(
            "ix_pedidos_sede_estado_creado",
            "sede_id",
            "estado",
            "creado_en",
        ),
        Index(
            "ix_pedidos_sede_estado_cerrado",
            "sede_id",
            "estado",
            "cerrado_en",
        ),
        CheckConstraint(
            "medio_pago IS NULL OR medio_pago IN ('EFECTIVO', 'TARJETA')",
            name="ck_pedidos_medio_pago_valido",
        ),
        CheckConstraint(
            "(estado = 'ABIERTO' AND medio_pago IS NULL AND cerrado_por IS NULL "
            "AND cerrado_en IS NULL) OR (estado = 'CERRADO' "
            "AND medio_pago IS NOT NULL AND cerrado_por IS NOT NULL "
            "AND cerrado_en IS NOT NULL)",
            name="ck_pedidos_cierre_consistente",
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
    medio_pago = Column(String(20), nullable=True)
    cerrado_por = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="RESTRICT"),
        nullable=True,
    )
    cerrado_en = Column(DateTime(timezone=True), nullable=True)
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
        CheckConstraint(
            "precio_compra_unitario >= 0",
            name="ck_linea_pedido_precio_compra_no_negativo",
        ),
        Index("ix_lineas_pedido_pedido_id", "pedido_id"),
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
    precio_compra_unitario = Column(Numeric(12, 2), nullable=False)
    codigo_producto = Column(String(40), nullable=False)
    nombre_producto = Column(String(120), nullable=False)
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
