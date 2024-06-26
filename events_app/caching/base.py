import aioredis
from events_app.core.config import Config
from events_app.utils.constants import REDIS


def get_redis_client(config: Config) -> aioredis.StrictRedis:
    return aioredis.Redis(
        host=config.data[REDIS]["host"],
        port=config.data[REDIS]["port"],
        password=config.data[REDIS]["password"],
        encoding="utf-8",
        decode_responses=True,
    )
