from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect


def test_hu37_alembic_upgrade_downgrade_upgrade_on_empty_schema(db_engine):
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))

    with db_engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")

        table_names = inspect(connection).get_table_names()
        assert "usuarios" not in table_names
        assert "pedidos" not in table_names

        command.upgrade(config, "head")
        upgraded_tables = set(inspect(connection).get_table_names())
        assert {
            "usuarios",
            "sesiones_activas",
            "sedes",
            "mesas",
            "proveedores",
            "productos",
            "inventarios",
            "pedidos",
            "lineas_pedido",
        } <= upgraded_tables

        indexes = inspect(connection).get_indexes("pedidos")
        open_order_index = next(
            index
            for index in indexes
            if index["name"] == "uq_pedidos_mesa_abierto"
        )
        assert open_order_index["unique"] is True
        assert "ABIERTO" in open_order_index["dialect_options"]["postgresql_where"]
