from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.adapters.out.postgres.models import OrderModel
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order_status import OrderStatus


@dataclass(frozen=True)
class OrderDto:
    """DTO незавершенного заказа для оперативного отображения на карте."""

    id: UUID
    location: Location


class GetNotCompletedOrdersQuery:
    """Query получения всех незавершенных заказов."""

    @staticmethod
    def create() -> Result[GetNotCompletedOrdersQuery, Error]:
        return Result.success(GetNotCompletedOrdersQuery())


class GetNotCompletedOrdersQueryHandler:
    """Обработчик Query получения всех незавершенных заказов."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def handle(
        self,
        query: GetNotCompletedOrdersQuery,
    ) -> Result[list[OrderDto], Error]:
        statuses = (OrderStatus.CREATED.name, OrderStatus.ASSIGNED.name)
        result = await self._session.execute(
            select(
                OrderModel.id,
                OrderModel.location_x,
                OrderModel.location_y,
            )
            .where(OrderModel.status.in_(statuses))
            .order_by(OrderModel.id),
        )

        rows = result.all()
        dtos = [
            OrderDto(
                id=row.id,
                location=Location.must_create(row.location_x, row.location_y),
            )
            for row in rows
        ]

        return Result.success(dtos)
