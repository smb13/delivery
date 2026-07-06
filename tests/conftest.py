from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from testcontainers.postgres import PostgresContainer

from libs.errs.result import Result
from microarch.delivery.config.container import Container, create_schema, drop_schema
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.ports.geo_client import IGeoClient
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork
from microarch.delivery.main import create_app


@pytest.fixture(scope="session")
def postgres_container() -> PostgresContainer:
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def postgres_url(postgres_container: PostgresContainer) -> str:
    connection_url = postgres_container.get_connection_url()
    return connection_url.replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://",
    ).replace("postgresql://", "postgresql+asyncpg://")


@pytest_asyncio.fixture(loop_scope="function")
async def engine(postgres_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_async_engine(postgres_url, echo=False)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest_asyncio.fixture(loop_scope="function")
async def uow(engine: AsyncEngine) -> AsyncIterator[IUnitOfWork]:
    await drop_schema(engine)
    await create_schema(engine)
    container = Container(engine)
    async with container.create_unit_of_work() as uow:
        yield uow


@pytest_asyncio.fixture(loop_scope="function")
async def client(engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    await drop_schema(engine)
    await create_schema(engine)

    geo_client = AsyncMock(spec=IGeoClient)
    geo_client.get_location.return_value = Result.success(Location.must_create(5, 5))

    app = create_app(engine=engine, geo_client=geo_client)
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client
