"""Create the schema for Sprints 1 through 4.

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-06
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("identificacion", sa.String(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column("nombre_usuario", sa.String(length=50), nullable=False),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("hashed_password", sa.String(), nullable=False),
        sa.Column("estado", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("es_admin", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("es_mesero", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("es_cajero", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.UniqueConstraint("identificacion", name="uq_usuarios_identificacion"),
        sa.UniqueConstraint("nombre_usuario", name="uq_usuarios_nombre_usuario"),
        sa.UniqueConstraint("email", name="uq_usuarios_email"),
    )
    op.create_index("ix_usuarios_identificacion", "usuarios", ["identificacion"])
    op.create_index("ix_usuarios_nombre_usuario", "usuarios", ["nombre_usuario"])
    op.create_index("ix_usuarios_email", "usuarios", ["email"])

    op.create_table(
        "sedes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(), nullable=False),
        sa.Column("nombre", sa.String(), nullable=False),
        sa.Column(
            "direccion",
            sa.String(length=200),
            nullable=False,
            server_default="Por definir",
        ),
        sa.Column("estado", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("codigo", name="uq_sedes_codigo"),
    )
    op.create_index("ix_sedes_codigo", "sedes", ["codigo"])

    op.create_table(
        "proveedores",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.UniqueConstraint("nombre", name="uq_proveedores_nombre"),
    )

    op.create_table(
        "mesas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("numero", sa.Integer(), nullable=False),
        sa.Column("estado", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("sede_id", "numero", name="uq_mesas_sede_numero"),
    )

    op.create_table(
        "usuario_sedes",
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("usuario_id", "sede_id"),
    )

    op.create_table(
        "sesiones_activas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("jti", sa.String(length=128), nullable=False),
        sa.Column("creada_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ultima_actividad", sa.DateTime(timezone=True), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("revocada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sede_seleccionada_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["sede_seleccionada_id"], ["sedes.id"], ondelete="SET NULL"
        ),
        sa.UniqueConstraint("jti", name="uq_sesiones_activas_jti"),
    )
    op.create_index(
        "ix_sesiones_activas_usuario_activa",
        "sesiones_activas",
        ["usuario_id", "activa"],
    )

    op.create_table(
        "productos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(length=40), nullable=False),
        sa.Column("nombre", sa.String(length=120), nullable=False),
        sa.Column("precio_venta", sa.Numeric(12, 2), nullable=False),
        sa.Column("precio_compra", sa.Numeric(12, 2), nullable=False),
        sa.Column("estado", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("proveedor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["proveedor_id"], ["proveedores.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint("codigo", name="uq_productos_codigo"),
    )
    op.create_index("ix_productos_codigo", "productos", ["codigo"])

    op.create_table(
        "inventarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint("cantidad >= 0", name="ck_inventario_cantidad_no_negativa"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["producto_id"], ["productos.id"], ondelete="RESTRICT"
        ),
        sa.UniqueConstraint(
            "sede_id", "producto_id", name="uq_inventario_sede_producto"
        ),
    )

    op.create_table(
        "pedidos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("sede_id", sa.Integer(), nullable=False),
        sa.Column("mesa_id", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(length=20), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sede_id"], ["sedes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["mesa_id"], ["mesas.id"], ondelete="RESTRICT"),
    )
    op.create_index(
        "uq_pedidos_mesa_abierto",
        "pedidos",
        ["mesa_id"],
        unique=True,
        postgresql_where=sa.column("estado") == "ABIERTO",
    )

    op.create_table(
        "lineas_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), nullable=False),
        sa.Column("producto_id", sa.Integer(), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("precio_unitario", sa.Numeric(12, 2), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "cantidad > 0", name="ck_linea_pedido_cantidad_positiva"
        ),
        sa.CheckConstraint(
            "precio_unitario >= 0",
            name="ck_linea_pedido_precio_no_negativo",
        ),
        sa.ForeignKeyConstraint(["pedido_id"], ["pedidos.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["producto_id"], ["productos.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="RESTRICT"),
    )


def downgrade() -> None:
    op.drop_table("lineas_pedido")
    op.drop_index("uq_pedidos_mesa_abierto", table_name="pedidos")
    op.drop_table("pedidos")
    op.drop_table("inventarios")
    op.drop_index("ix_productos_codigo", table_name="productos")
    op.drop_table("productos")
    op.drop_index("ix_sesiones_activas_usuario_activa", table_name="sesiones_activas")
    op.drop_table("sesiones_activas")
    op.drop_table("usuario_sedes")
    op.drop_table("mesas")
    op.drop_table("proveedores")
    op.drop_index("ix_sedes_codigo", table_name="sedes")
    op.drop_table("sedes")
    op.drop_index("ix_usuarios_email", table_name="usuarios")
    op.drop_index("ix_usuarios_nombre_usuario", table_name="usuarios")
    op.drop_index("ix_usuarios_identificacion", table_name="usuarios")
    op.drop_table("usuarios")
