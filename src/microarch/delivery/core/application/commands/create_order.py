from __future__ import annotations

import random
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from libs.errs.error import Error
from libs.errs.guard import Guard
from libs.errs.result import Result
from microarch.delivery.core.domain.model.address import Address
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.volume import Volume
from microarch.delivery.core.ports.order_repository import IOrderRepository

_LOCATION_MIN = 1
_LOCATION_MAX = 10


@dataclass(frozen=True)
class CreateOrderCommand:
    """Команда создания заказа."""

    order_id: UUID
    address: Address
    volume: int

    @staticmethod
    def create(
        order_id: UUID,
        address: Address,
        volume: int,
    ) -> Result[CreateOrderCommand, Error]:
        err = Guard.combine(
            Guard.against_none_or_empty_uuid(order_id, "order_id"),
            Guard.against_none(address, "address"),
            Guard.against_less_or_equal(volume, 0, "volume"),
        )
        if err is not None:
            return Result.failure(err)

        return Result.success(
            CreateOrderCommand(
                order_id=order_id,
                address=address,
                volume=volume,
            ),
        )


class CreateOrderCommandHandler:
    """Обработчик команды создания заказа."""

    def __init__(
        self,
        order_repository: IOrderRepository,
        session: AsyncSession,
    ) -> None:
        self._order_repository = order_repository
        self._session = session

    async def handle(self, command: CreateOrderCommand) -> Result[UUID, Error]:
        location = Location.must_create(
            random.randint(_LOCATION_MIN, _LOCATION_MAX),
            random.randint(_LOCATION_MIN, _LOCATION_MAX),
        )

        volume_result = Volume.create(command.volume)
        if volume_result.is_failure:
            return Result.failure(volume_result.get_error())

        order_result = Order.create(
            command.order_id,
            location,
            volume_result.get_value(),
        )
        if order_result.is_failure:
            return Result.failure(order_result.get_error())

        order = order_result.get_value()
        await self._order_repository.add(order)
        await self._session.commit()

        return Result.success(order.id)
