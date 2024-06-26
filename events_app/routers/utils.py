import json
import logging
from datetime import datetime
from typing import List

import aioredis
from events_app.database_manager.schemas import EventSchema
from events_app.pyd_models.events import EventModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


logging.basicConfig(level=logging.INFO)


async def get_events_from_redis(redis_key: str, redis_client: aioredis.Redis):
    """
    Retrieves events data from Redis cache.

    Args:
        redis_key (str): The key used to retrieve cached events.
        redis_client (aioredis.Redis): Redis client for asynchronous operations.

    Returns:
        Optional[bytes]: The cached data if available, None otherwise.
    """
    logging.info(f"Attempting to retrieve cached data for key: {redis_key}")
    try:
        cached_data = await redis_client.get(redis_key)
        if cached_data:
            logging.info("Cache hit - data found for key: {}".format(redis_key))
            return cached_data
        logging.info("Cache miss - no data found for key: {}".format(redis_key))
    except Exception as e:
        logging.error(f"Failed to retrieve data from Redis: {e}")
    return None


async def get_events_from_db(starts_at: datetime, ends_at: datetime, async_session: AsyncSession):
    """
    Fetches events from the database_manager within a specific start and end datetime.

    Args:
        starts_at (datetime): Start datetime to filter events.
        ends_at (datetime): End datetime to filter events.
        async_session (AsyncSession): SQLAlchemy async session for database_manager operations.

    Returns:
        List[EventSchema]: A list of event records from the database_manager.
    """
    logging.info("Querying database_manager for events.")
    try:
        fetch_events_query = await async_session.execute(
            select(EventSchema).filter(
                EventSchema.start_date_time >= starts_at,
                EventSchema.end_date_time <= ends_at,
            )
        )
        events = fetch_events_query.scalars().all()
        logging.info(f"Retrieved {len(events)} events from the database_manager.")
        return events
    except Exception as e:
        logging.error(f"Database query failed: {e}")
        return []


async def set_events_in_redis(
    redis_key: str, event_schemas: List[EventSchema], redis_client: aioredis.Redis
):
    """
    Serializes and sets events data in Redis.

    Args:
        redis_key (str): The key under which to store the events data.
        event_schemas (List[EventSchema]): List of event schemas to serialize and store.
        redis_client (aioredis.Redis): Redis client for asynchronous operations.

    Raises:
        Exception: If there is a failure in setting the data in Redis.
    """
    logging.info(f"Setting events data in Redis under key: {redis_key}")
    try:
        redis_events = [
            EventModel.model_validate(event_schema).model_dump_json()
            for event_schema in event_schemas
        ]
        await redis_client.set(redis_key, json.dumps(redis_events))
        logging.info("Events data successfully set in Redis.")
    except Exception as err:
        logging.error(f"Failed to set data in Redis: {err}")
