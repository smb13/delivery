from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.out.postgres.courier_repository import CourierRepository
from microarch.delivery.adapters.out.postgres.order_repository import OrderRepository
from microarch.delivery.core.ports.courier_repository import ICourierRepository
from microarch.delivery.core.ports.order_repository import IOrderRepository
from microarch.delivery.core.ports.unit_of_work import IUnitOfWork


class UnitOfWork(IUnitOfWork):
    """Postgres-адаптер Unit Of Work.

    Оборачивает AsyncSession SQLAlchemy и обеспечивает атомарное
    сохранение нескольких агрегатов в рамках одной транзакции.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._orders = OrderRepository(session)
        self._couriers = CourierRepository(session)

    @property
    def orders(self) -> IOrderRepository:
        return self._orders

    @property
    def couriers(self) -> ICourierRepository:
        return self._couriers

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self._session.close()
        return False
