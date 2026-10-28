"""Add optional contact number to suppliers.

Revision ID: 0002_proveedor_contacto
Revises: 0001_initial
Create Date: 2026-10-07
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_proveedor_contacto"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Añade a proveedores un número de contacto opcional."""
    op.add_column(
        "proveedores",
        sa.Column("numero_contacto", sa.String(length=30), nullable=True),
    )


def downgrade() -> None:
    """Elimina el campo de contacto al revertir la revisión."""
    op.drop_column("proveedores", "numero_contacto")
