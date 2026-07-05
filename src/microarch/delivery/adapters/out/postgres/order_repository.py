from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.out.postgres.mappers import OrderMapper
from microarch.delivery.adapters.out.postgres.models import OrderModel
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.order.order_status import OrderStatus
from microarch.delivery.core.ports.order_repository import IOrderRepository


class OrderRepository(IOrderRepository):
    """Postgres-адаптер репозитория заказов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, order: Order) -> None:
        model = OrderMapper.to_model(order)
        self._session.add(model)

    async def update(self, order: Order) -> None:
        model = OrderMapper.to_model(order)
        await self._session.merge(model)

    async def get(self, order_id: UUID) -> Order | None:
        model = await self._session.get(OrderModel, order_id)
        if model is None:
            return None
        return OrderMapper.to_domain(model)

    async def get_one_created(self) -> Order | None:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.status == OrderStatus.CREATED.name)
            .order_by(OrderModel.id)
            .limit(1),
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return OrderMapper.to_domain(model)

    async def get_all_assigned(self) -> list[Order]:
        result = await self._session.execute(
            select(OrderModel)
            .where(OrderModel.status == OrderStatus.ASSIGNED.name)
            .order_by(OrderModel.id),
        )
        return [OrderMapper.to_domain(model) for model in result.scalars().all()]
