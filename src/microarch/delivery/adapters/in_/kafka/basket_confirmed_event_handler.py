from __future__ import annotations

import logging
from uuid import UUID

from google.protobuf.message import DecodeError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from microarch.delivery.adapters.in_.kafka import basket_events_pb2
from microarch.delivery.adapters.out.postgres.order_repository import OrderRepository
from microarch.delivery.core.application.commands.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
)
from microarch.delivery.core.domain.model.address import Address
from microarch.delivery.core.ports.geo_client import IGeoClient

logger = logging.getLogger(__name__)


class BasketConfirmedIntegrationEventHandler:
    """Обработчик интеграционного события подтверждения корзины.

    Преобразует BasketConfirmedIntegrationEvent в команду создания заказа
    и выполняет ее в рамках отдельной сессии БД.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        geo_client: IGeoClient,
    ) -> None:
        self._session_factory = session_factory
        self._geo_client = geo_client

    async def handle(self, raw_event: bytes) -> None:
        """Десериализует событие и создает заказ."""
        event = basket_events_pb2.BasketConfirmedIntegrationEvent()
        try:
            event.ParseFromString(raw_event)
        except DecodeError:
            logger.exception("Failed to decode BasketConfirmedIntegrationEvent")
            return

        try:
            order_id = UUID(event.basket_id)
        except ValueError:
            logger.exception("Invalid basket_id UUID: %s", event.basket_id)
            return

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
            return

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
            return

        async with self._session_factory() as session:
            handler = CreateOrderCommandHandler(
                order_repository=OrderRepository(session),
                geo_client=self._geo_client,
                session=session,
            )
            result = await handler.handle(command_result.get_value())
            if result.is_failure:
                logger.error(
                    "Failed to create order from basket event: %s",
                    result.get_error(),
                )
