from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from microarch.delivery.adapters.out.postgres.models import Base
from microarch.delivery.adapters.out.postgres.unit_of_work import UnitOfWork
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork


class Container:
    """Простая фабрика для создания инфраструктурных объектов сервиса."""

    def __init__(self, engine: AsyncEngine) -> None:
        self._engine = engine
        self._session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    def create_unit_of_work(self) -> IUnitOfWork:
        session = self._session_factory()
        return UnitOfWork(session)


async def create_schema(engine: AsyncEngine) -> None:
    """Создает все таблицы по ORM-моделям. Используется в тестах."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_schema(engine: AsyncEngine) -> None:
    """Удаляет все таблицы по ORM-моделям. Используется в тестах."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
