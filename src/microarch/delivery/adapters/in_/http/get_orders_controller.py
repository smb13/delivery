from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.api.get_orders_api_base import BaseGetOrdersApi
from microarch.delivery.adapters.in_.http.dependencies import bad_request, conflict
from microarch.delivery.adapters.in_.http.models.location import Location as LocationModel
from microarch.delivery.adapters.in_.http.models.order import Order as OrderModel
from microarch.delivery.core.application.queries.get_not_completed_orders import (
    GetNotCompletedOrdersQuery,
    GetNotCompletedOrdersQueryHandler,
)


class GetOrdersController(BaseGetOrdersApi):
    """Контроллер получения всех незавершенных заказов."""

    async def get_orders(self, session: AsyncSession) -> list[OrderModel]:
        query_result = GetNotCompletedOrdersQuery.create()
        if query_result.is_failure:
            return bad_request(query_result.get_error())

        handler = GetNotCompletedOrdersQueryHandler(session=session)
        result = await handler.handle(query_result.get_value())
        if result.is_failure:
            return conflict(result.get_error())

        return [
            OrderModel(
                id=dto.id,
                location=LocationModel(x=dto.location.x, y=dto.location.y),
            )
            for dto in result.get_value()
        ]
