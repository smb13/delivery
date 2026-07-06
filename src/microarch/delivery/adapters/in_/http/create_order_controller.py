from __future__ import annotations

from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from microarch.delivery.adapters.in_.http.api.create_order_api_base import (
    BaseCreateOrderApi,
)
from microarch.delivery.adapters.in_.http.dependencies import bad_request, conflict
from microarch.delivery.adapters.in_.http.models.create_order_response import (
    CreateOrderResponse,
)
from microarch.delivery.adapters.in_.http.models.new_order import NewOrder
from microarch.delivery.adapters.out.postgres.order_repository import OrderRepository
from microarch.delivery.core.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
)
from microarch.delivery.core.domain.model.address import Address as DomainAddress
from microarch.delivery.core.ports.geo_client import IGeoClient


class CreateOrderController(BaseCreateOrderApi):
    """Контроллер создания заказа."""

    async def create_order(
        self,
        new_order: NewOrder,
        session: AsyncSession,
        geo_client: IGeoClient,
    ) -> CreateOrderResponse:
        address_result = DomainAddress.create(
            country=new_order.address.country,
            city=new_order.address.city,
            street=new_order.address.street,
            house=new_order.address.house,
            apartment=new_order.address.apartment,
        )
        if address_result.is_failure:
            return bad_request(address_result.get_error())

        command_result = CreateOrderCommand.create(
            order_id=new_order.id,
            address=address_result.get_value(),
            volume=new_order.volume,
        )
        if command_result.is_failure:
            return bad_request(command_result.get_error())

        handler = CreateOrderCommandHandler(
            order_repository=OrderRepository(session),
            geo_client=geo_client,
            session=session,
        )
        result = await handler.handle(command_result.get_value())
        if result.is_failure:
            return conflict(result.get_error())

        response_model = CreateOrderResponse(order_id=result.get_value())
        return JSONResponse(
            status_code=201,
            content=response_model.model_dump(mode="json", by_alias=True),
        )
