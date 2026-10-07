"""Configura Alembic con metadatos ORM y conexión por entorno o tests."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.database import Base
from app.core.settings import DATABASE_URL
from app.auth import models as auth_models
from app.sedes import models as site_models
from app.usuarios import models as user_models
from app.catalogo import models as catalog_models
from app.inventario import models as inventory_models
from app.ventas import models as order_models

MODEL_MODULES = (
    auth_models,
    site_models,
    user_models,
    catalog_models,
    inventory_models,
    order_models,
)
# Importar todos los modelos registra sus tablas antes de que Alembic compare metadatos.

config = context.config
database_url = config.get_main_option("sqlalchemy.url")
if database_url == "postgresql+psycopg://":
    database_url = DATABASE_URL
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Genera/ejecuta migraciones usando URL y SQL literal sin abrir conexión."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica migraciones mediante conexión activa o una conexión propia."""
    supplied_connection = config.attributes.get("connection")
    if supplied_connection is not None:
        context.configure(
            connection=supplied_connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()
        return

    connectable = engine_from_config(
        {"sqlalchemy.url": database_url},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
