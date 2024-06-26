import logging
from contextlib import asynccontextmanager

import sentry_sdk
from cron.schedular import start_scheduler
from events_app.caching.base import get_redis_client

# from events_app.api.healthcheck import healthcheck_router
from events_app.core.config import Config
from events_app.core.config import get_config
from events_app.database_manager.base import create_database
from events_app.database_manager.base import engine_kw
from events_app.database_manager.base import get_db_url
from events_app.database_manager.session_manager.db_session import Database
from events_app.routers.events import events_router
from events_app.routers.healthcheck import health_router
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def register_routers(app: FastAPI):
    # include all routers
    app.include_router(health_router)
    app.include_router(events_router)


def register_sentry(config: Config):
    sentry_sdk.init(
        dsn=config.data["sentry"]["dsn"],
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=1.0,
        environment=config.data["sentry"]["environment"],
    )


def get_app(config_file) -> FastAPI:
    config = get_config(config_file)
    app = FastAPI(
        title="Market Place Events", lifespan=lifespan
    )  # change debug based on environment
    # register_sentry(config)
    app.state.config = config
    # Add middleware, event handlers, etc. here
    # Include routers
    register_routers(app)

    # Set up CORS middleware
    origins = [
        "http://localhost:8000",  # For local development
        # Add any other origins as needed
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


@asynccontextmanager
async def lifespan(app):
    logging.info("Application startup")
    await create_database(app.state.config)
    # TODO: apply_migration not working
    # run_apply_migration(events_app.state.config)

    async_db_url = get_db_url(app.state.config)
    Database.init(async_db_url, engine_kw=engine_kw)
    logging.info("Initialized database_manager")

    async_redis_client = get_redis_client(app.state.config)
    logging.info("Initialized redis")
    app.state.async_redis_client = async_redis_client
    logging.info("start schedular cron job")
    start_scheduler()

    try:
        yield
    finally:
        logging.info("Application shutdown")

        # Close the connection when the application shuts down
        await app.state.async_redis_client.close()
