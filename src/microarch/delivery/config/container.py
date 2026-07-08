from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from libs.ddd.domain_event_publisher import DomainEventPublisher
from microarch.delivery.adapters.out.postgres.models import Base
from microarch.delivery.adapters.out.postgres.unit_of_work import UnitOfWork
from microarch.delivery.core.application.commands.assign_order import (
    AssignOrderCommandHandler,
)
from microarch.delivery.core.domain.services.orders_distribution_service_impl import (
    OrdersDistributionServiceImpl,
)
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

    def create_assign_order_handler(
        self,
        uow: IUnitOfWork,
        domain_event_publisher: DomainEventPublisher,
    ) -> AssignOrderCommandHandler:
        """Создает обработчик назначения заказа на основе переданной UoW."""
        return AssignOrderCommandHandler(
            order_repository=uow.orders,
            courier_repository=uow.couriers,
            distribution_service=OrdersDistributionServiceImpl(),
            unit_of_work=uow,
            domain_event_publisher=domain_event_publisher,
        )


async def create_schema(engine: AsyncEngine) -> None:
    """Создает все таблицы по ORM-моделям. Используется в тестах."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_schema(engine: AsyncEngine) -> None:
    """Удаляет все таблицы по ORM-моделям. Используется в тестах."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
