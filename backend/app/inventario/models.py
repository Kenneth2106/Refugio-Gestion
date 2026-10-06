from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from app.core.database import Base


class Inventario(Base):
    __tablename__ = "inventarios"
    __table_args__ = (
        UniqueConstraint("sede_id", "producto_id", name="uq_inventario_sede_producto"),
        CheckConstraint("cantidad >= 0", name="ck_inventario_cantidad_no_negativa"),
    )

    id = Column(Integer, primary_key=True)
    sede_id = Column(
        Integer,
        ForeignKey("sedes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    producto_id = Column(
        Integer,
        ForeignKey("productos.id", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad = Column(Integer, nullable=False, default=0)

    sede = relationship("Sede")
    producto = relationship("Producto")
