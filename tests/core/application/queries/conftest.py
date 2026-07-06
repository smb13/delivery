from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from microarch.delivery.config.container import create_schema, drop_schema


@pytest_asyncio.fixture(loop_scope="function", autouse=True)
async def _clean_schema(engine: AsyncEngine) -> AsyncIterator[None]:
    await drop_schema(engine)
    await create_schema(engine)
    yield


@pytest_asyncio.fixture(loop_scope="function")
async def query_session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_maker() as session:
        yield session
