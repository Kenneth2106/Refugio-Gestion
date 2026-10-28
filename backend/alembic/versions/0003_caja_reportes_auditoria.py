"""Add payment, historical sale details and audit events.

Revision ID: 0003_caja_reportes_auditoria
Revises: 0002_proveedor_contacto
Create Date: 2026-10-27
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_caja_reportes_auditoria"
down_revision = "0002_proveedor_contacto"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Añade cierre de caja, precios históricos y eventos de auditoría."""
    op.add_column("pedidos", sa.Column("medio_pago", sa.String(length=20)))
    op.add_column("pedidos", sa.Column("cerrado_por", sa.Integer(), nullable=True))
    op.add_column(
        "pedidos",
        sa.Column("cerrado_en", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_pedidos_cerrado_por_usuarios",
        "pedidos",
        "usuarios",
        ["cerrado_por"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_pedidos_sede_estado_creado",
        "pedidos",
        ["sede_id", "estado", "creado_en"],
    )
    op.create_index(
        "ix_pedidos_sede_estado_cerrado",
        "pedidos",
        ["sede_id", "estado", "cerrado_en"],
    )
    op.create_check_constraint(
        "ck_pedidos_medio_pago_valido",
        "pedidos",
        "medio_pago IS NULL OR medio_pago IN ('EFECTIVO', 'TARJETA')",
    )
    op.create_index(
        "ix_lineas_pedido_pedido_id",
        "lineas_pedido",
        ["pedido_id"],
    )
    op.create_check_constraint(
        "ck_pedidos_cierre_consistente",
        "pedidos",
        "(estado = 'ABIERTO' AND medio_pago IS NULL AND cerrado_por IS NULL "
        "AND cerrado_en IS NULL) OR (estado = 'CERRADO' "
        "AND medio_pago IS NOT NULL AND cerrado_por IS NOT NULL "
        "AND cerrado_en IS NOT NULL)",
    )

    op.add_column(
        "lineas_pedido",
        sa.Column("precio_compra_unitario", sa.Numeric(12, 2), nullable=True),
    )
    op.add_column(
        "lineas_pedido",
        sa.Column("codigo_producto", sa.String(length=40), nullable=True),
    )
    op.add_column(
        "lineas_pedido",
        sa.Column("nombre_producto", sa.String(length=120), nullable=True),
    )
    op.execute(
        """
        UPDATE lineas_pedido
        SET precio_compra_unitario = productos.precio_compra,
            codigo_producto = productos.codigo,
            nombre_producto = productos.nombre
        FROM productos
        WHERE lineas_pedido.producto_id = productos.id
        """
    )
    op.alter_column("lineas_pedido", "precio_compra_unitario", nullable=False)
    op.alter_column("lineas_pedido", "codigo_producto", nullable=False)
    op.alter_column("lineas_pedido", "nombre_producto", nullable=False)
    op.create_check_constraint(
        "ck_linea_pedido_precio_compra_no_negativo",
        "lineas_pedido",
        "precio_compra_unitario >= 0",
    )

    op.create_table(
        "eventos_auditoria",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("sede_id", sa.Integer(), nullable=True),
        sa.Column("pedido_id", sa.Integer(), nullable=True),
        sa.Column("accion", sa.String(length=40), nullable=False),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(["actor_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"], ondelete="SET NULL"),
    )
    op.create_index(
        "ix_eventos_auditoria_creado_en",
        "eventos_auditoria",
        ["creado_en"],
    )


def downgrade() -> None:
    """Revierte los campos de caja y la tabla de auditoría."""
    op.drop_index("ix_eventos_auditoria_creado_en", table_name="eventos_auditoria")
    op.drop_table("eventos_auditoria")
    op.drop_index("ix_lineas_pedido_pedido_id", table_name="lineas_pedido")
    op.drop_constraint(
        "ck_linea_pedido_precio_compra_no_negativo",
        "lineas_pedido",
        type_="check",
    )
    op.drop_index("ix_pedidos_sede_estado_cerrado", table_name="pedidos")
    op.drop_index("ix_pedidos_sede_estado_creado", table_name="pedidos")
    op.drop_column("lineas_pedido", "nombre_producto")
    op.drop_column("lineas_pedido", "codigo_producto")
    op.drop_column("lineas_pedido", "precio_compra_unitario")
    op.drop_constraint("ck_pedidos_cierre_consistente", "pedidos", type_="check")
    op.drop_constraint("ck_pedidos_medio_pago_valido", "pedidos", type_="check")
    op.drop_constraint(
        "fk_pedidos_cerrado_por_usuarios",
        "pedidos",
        type_="foreignkey",
    )
    op.drop_column("pedidos", "cerrado_en")
    op.drop_column("pedidos", "cerrado_por")
    op.drop_column("pedidos", "medio_pago")
