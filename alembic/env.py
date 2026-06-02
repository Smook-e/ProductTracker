import asyncio
from logging.config import fileConfig
import os
from dotenv import load_dotenv

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# 1. IMPORT YOUR BASE AND MODELS HERE EXACTLY
from database import Base
from models import Product, PriceHistory, User # Adjust 'models' if your file has a different name

load_dotenv()

# This is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Provide Alembic access to your registered model metadata
target_metadata = Base.metadata

# Use your ASYNC environment variable for migrations
ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL")
config.set_main_option("sqlalchemy.url", ASYNC_DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        compare_type=True,  
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    """Helper context runner to execute sync commands on the async connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using an AsyncEngine."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # This executes the async online migration framework loop
    asyncio.run(run_migrations_online())
