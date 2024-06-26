import argparse
import asyncio
import logging.config
import os
import pathlib
import sys

import uvicorn
from events_app.create_app import get_app
from events_app.utils.constants import ConfigFile


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def build_app(config_file):
    app = get_app(config_file)
    return app


def main(args):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    logger = logging.getLogger(__name__)
    logger.info(
        "Fever App starting up",
    )
    app = loop.run_until_complete(build_app(args.config))

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        log_level="debug",
    )
    return 0


def parser(config):
    rv = argparse.ArgumentParser(usage=__doc__)
    rv.add_argument(
        "--config",
        required=False,
        help="Set the path to a configuration file (TOML) ",
        default=config,
        type=pathlib.Path,
    )
    return rv


def run():
    default_config = ConfigFile.PRODUCTION
    p = parser(default_config)
    args = p.parse_args()
    try:
        rv = main(args)
        sys.exit(rv)
    except Exception as e:
        logging.error(f"Error running fastapi: {e}")


if __name__ == "__main__":
    run()
