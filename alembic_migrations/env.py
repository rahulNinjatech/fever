import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from events_app.core.config import get_config
from events_app.database_manager import Base
from events_app.database_manager.base import get_db_url
from events_app.database_manager.schemas import *  # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
from events_app.utils.constants import ConfigFile
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine


config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    # connection -> transaction -> sessions
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    _config = get_config(ConfigFile.TEST)

    async_db_url = get_db_url(_config)
    # Create SQLAlchemy engine
    async_engine = create_async_engine(async_db_url)

    # Create a connection
    async with async_engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await async_engine.dispose()


def run_migrations_online():
    """Determine if we are in an async context and run the migrations accordingly."""
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            # If an event loop is running, create a task
            return asyncio.create_task(run_async_migrations_online())
    except RuntimeError:
        pass
    except Exception as e:
        logging.error(f"Error while applying database migration: {e}", exc_info=True)

    try:
        # If no event loop is running, use asyncio.run()
        asyncio.run(run_async_migrations_online())
    except Exception as e:
        logging.error(f"Error while applying database migration: {e}", exc_info=True)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations_online())
    # # Ensure this is called within an async context
    # run_migrations_online()
