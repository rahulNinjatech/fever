from aioredis import Redis
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from httpx import AsyncClient
from httpx import Limits
from sqlalchemy.ext.asyncio import AsyncSession


def get_app(request: Request) -> FastAPI:
    return request.app


async def get_config(app: FastAPI = Depends(get_app)):
    yield app.state.config


async def get_async_session(app: FastAPI = Depends(get_app)) -> AsyncSession:
    async_session = app.state.async_session_maker()
    yield async_session


async def get_async_redis_client(app: FastAPI = Depends(get_app)) -> Redis:
    yield app.state.async_redis_client


async def get_async_httpx_client() -> AsyncClient:
    limits = Limits(max_connections=10, max_keepalive_connections=5)
    client = AsyncClient(http2=True, limits=limits)
    try:
        yield client
    finally:
        await client.aclose()
