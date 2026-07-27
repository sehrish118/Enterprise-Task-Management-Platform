#Alembic migration environment — configured for sync SQLAlchemy.


# from logging.config import fileConfig

# from sqlalchemy import engine_from_config
# from sqlalchemy import pool

# from alembic import context

# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config

# # Interpret the config file for Python logging.
# # This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# # add your model's MetaData object here
# # for 'autogenerate' support
# # from myapp import mymodel
# # target_metadata = mymodel.Base.metadata
# target_metadata = None

# # other values from the config, defined by the needs of env.py,
# # can be acquired:
# # my_important_option = config.get_main_option("my_important_option")
# # ... etc.


# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode.

#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well.  By skipping the Engine creation
#     we don't even need a DBAPI to be available.

#     Calls to context.execute() here emit the given string to the
#     script output.

#     """
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )

#     with context.begin_transaction():
#         context.run_migrations()


# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode.

#     In this scenario we need to create an Engine
#     and associate a connection with the context.

#     """
#     connectable = engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )

#     with connectable.connect() as connection:
#         context.configure(
#             connection=connection, target_metadata=target_metadata
#         )

#         with context.begin_transaction():
#             context.run_migrations()


# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()


"""
Alembic migration environment — configured for async SQLAlchemy.

Key difference from default Alembic template: migrations run through
our async engine (asyncpg), not a sync one. Alembic's core migration
runner is still sync internally, so we bridge it using
run_sync() — this is the standard pattern for async SQLAlchemy + Alembic.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import settings
from app.db.base import Base
import app.models
from app.db.session import engine


# noqa: F401 — populates Base.metadata via app/models/__init__.py

# Alembic's config object — gives access to values in alembic.ini
config = context.config

# Wire our .env-driven DATABASE_URL into Alembic's config,
# overriding whatever (if anything) is in alembic.ini.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for logging (unchanged from default)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what powers `alembic revision --autogenerate` —
# Alembic compares this metadata against the live DB schema.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Generate SQL scripts without a live DB connection.
    Used for CI pipelines or generating .sql files to hand off to a DBA
    — not something we'll use day-to-day, but kept for completeness.
    """
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    The path we'll actually use — runs migrations against our live,
    already-configured async engine.
    """
    connectable: AsyncEngine = engine

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
