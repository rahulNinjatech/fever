import asyncio
import logging
import pathlib

import asyncpg
from alembic import command
from alembic.config import Config as AlembicConfig
from events_app.core.config import Config
from sqlalchemy.engine.url import URL


engine_kw = {
    # "echo": False,  # print all SQL statements
    "pool_pre_ping": True,
    # feature will normally emit SQL equivalent to “SELECT 1” each time a connection is checked out from the pool
    "pool_size": 2,  # number of connections to keep open at a time
    "max_overflow": 4,  # number of connections to allow to be opened above pool_size
    "connect_args": {
        "prepared_statement_cache_size": 0,  # disable prepared statement cache
        "statement_cache_size": 0,  # disable statement cache
    },
}


def get_db_url(config: Config) -> URL:
    config_db = config.data["db"]
    return URL.create(drivername="postgresql+asyncpg", **config_db)


async def create_database(config: Config):
    user = config.data["db"]["username"]
    password = config.data["db"]["password"]
    host = config.data["db"]["host"]
    port = config.data["db"]["port"]
    database = config.data["db"]["database"]

    try:
        # Connect to the PostgreSQL server
        conn = await asyncpg.connect(user=user, password=password, host=host, port=port)
        logging.info("Connected to the PostgreSQL server successfully")

    except Exception as e:
        logging.error(f"Error while connecting to the PostgreSQL server: {e}")
        return False

    try:
        # Create a new database_manager
        await conn.execute(f"CREATE DATABASE {database}")
        logging.info(f"Database {database} created")
    except asyncpg.exceptions.DuplicateDatabaseError:
        # Database already exists
        logging.warning(f"Database {database} already exists")

    # Close the connection
    await conn.close()


def apply_migration(config: Config):
    try:
        # Get the current file's directory
        current_dir = pathlib.Path(__file__).parent
        # Construct the path to the root directory
        root_dir = current_dir.parent.parent

        alembic_ini_path = f"{root_dir}/alembic.ini"
        alembic_migrations_path = f"{root_dir}/alembic"
        alembic_cfg = AlembicConfig(alembic_ini_path)
        alembic_cfg.set_main_option("script_location", alembic_migrations_path)
        db_url = str(get_db_url(config))
        alembic_cfg.set_main_option("sqlalchemy.url", db_url)
        command.upgrade(alembic_cfg, "head")
        logging.info("Database migration applied")
    except Exception as e:
        logging.error(f"Error while applying database_manager migration: {e}", exc_info=True)


def run_apply_migration(config: Config):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # No event loop is running
        loop = None

    if loop and loop.is_running():
        # If an event loop is running, create a task
        task = loop.create_task(apply_migration(config))
        loop.run_until_complete(task)
    else:
        # If no event loop is running, use asyncio.run()
        asyncio.run(apply_migration(config))
