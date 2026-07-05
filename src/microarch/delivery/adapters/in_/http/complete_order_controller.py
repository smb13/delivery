from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.api.complete_order_api_base import (
    BaseCompleteOrderApi,
)
from microarch.delivery.adapters.in_.http.dependencies import bad_request, conflict
from microarch.delivery.adapters.out.postgres.courier_repository import CourierRepository
from microarch.delivery.adapters.out.postgres.order_repository import OrderRepository
from microarch.delivery.adapters.out.postgres.unit_of_work import UnitOfWork
from microarch.delivery.core.application.commands.complete_order import (
    CompleteOrderCommand,
    CompleteOrderCommandHandler,
)


class CompleteOrderController(BaseCompleteOrderApi):
    """Контроллер завершения заказа."""

    async def complete_order(
        self,
        courierId: UUID,
        orderId: UUID,
        session: AsyncSession,
    ) -> None:
        command_result = CompleteOrderCommand.create(courierId, orderId)
        if command_result.is_failure:
            return bad_request(command_result.get_error())

        handler = CompleteOrderCommandHandler(
            order_repository=OrderRepository(session),
            courier_repository=CourierRepository(session),
            unit_of_work=UnitOfWork(session),
        )
        result = await handler.handle(command_result.get_value())
        if result.is_failure:
            return conflict(result.get_error())

        return None
