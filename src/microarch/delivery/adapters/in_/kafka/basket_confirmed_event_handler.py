from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from uuid import UUID

from google.protobuf.message import DecodeError

from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.adapters.in_.kafka import basket_events_pb2
from microarch.delivery.core.application.commands.create_order import (
    CreateOrderCommand,
)
from microarch.delivery.core.domain.model.address import Address

logger = logging.getLogger(__name__)


class BasketConfirmedIntegrationEventHandler:
    """Обработчик интеграционного события подтверждения корзины.

    Преобразует BasketConfirmedIntegrationEvent в команду создания заказа
    и вызывает переданный сценарий создания заказа.
    """

    def __init__(
        self,
        handle_create_order: Callable[
            [CreateOrderCommand],
            Awaitable[Result[UUID, Error]],
        ],
    ) -> None:
        self._handle_create_order = handle_create_order

    async def handle(self, raw_event: bytes) -> bool:
        """Десериализует событие и создает заказ.

        Returns:
            True, если заказ успешно создан, иначе False.
        """
        event = basket_events_pb2.BasketConfirmedIntegrationEvent()
        try:
            event.ParseFromString(raw_event)
        except DecodeError:
            logger.exception("Failed to decode BasketConfirmedIntegrationEvent")
            return False

        try:
            order_id = UUID(event.basket_id)
        except ValueError:
            logger.exception("Invalid basket_id UUID: %s", event.basket_id)
            return False

        address_result = Address.create(
            country=event.address.country,
            city=event.address.city,
            street=event.address.street,
            house=event.address.house,
            apartment=event.address.apartment,
        )
        if address_result.is_failure:
            logger.error(
                "Invalid address in basket confirmed event: %s",
                address_result.get_error(),
            )
            return False

        command_result = CreateOrderCommand.create(
            order_id=order_id,
            address=address_result.get_value(),
            volume=event.volume,
        )
        if command_result.is_failure:
            logger.error(
                "Invalid create order command: %s",
                command_result.get_error(),
            )
            return False

        result = await self._handle_create_order(command_result.get_value())
        if result.is_failure:
            logger.error(
                "Failed to create order from basket event: %s",
                result.get_error(),
            )
            return False

        return True
