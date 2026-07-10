from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from libs.errs.error import Error
from libs.errs.result import Result
from microarch.delivery.adapters.in_.kafka import (
    BasketConfirmedIntegrationEventHandler,
    basket_events_pb2,
)
from microarch.delivery.core.application.commands.create_order import (
    CreateOrderCommand,
)

pytestmark = pytest.mark.asyncio


def _build_event_bytes(
    basket_id: str,
    country: str = "RU",
    city: str = "Moscow",
    street: str = "Tverskaya",
    house: str = "1",
    apartment: str = "2",
    volume: int = 3,
) -> bytes:
    event = basket_events_pb2.BasketConfirmedIntegrationEvent(
        basket_id=basket_id,
        address=basket_events_pb2.Address(
            country=country,
            city=city,
            street=street,
            house=house,
            apartment=apartment,
        ),
        volume=volume,
    )
    return event.SerializeToString()


async def test_handler_calls_use_case_and_returns_true_on_success() -> None:
    handle_create_order = AsyncMock()
    handle_create_order.return_value = Result.success(uuid4())

    handler = BasketConfirmedIntegrationEventHandler(
        handle_create_order=handle_create_order,
    )

    order_id = uuid4()
    raw_event = _build_event_bytes(basket_id=str(order_id))

    success = await handler.handle(raw_event)

    assert success is True
    handle_create_order.assert_awaited_once()
    command = handle_create_order.await_args[0][0]
    assert isinstance(command, CreateOrderCommand)
    assert command.order_id == order_id
    assert command.address.country == "RU"
    assert command.volume == 3


async def test_handler_returns_false_when_use_case_fails() -> None:
    handle_create_order = AsyncMock()
    handle_create_order.return_value = Result.failure(
        Error.of("order.already.exists", "Order already exists"),
    )

    handler = BasketConfirmedIntegrationEventHandler(
        handle_create_order=handle_create_order,
    )

    order_id = uuid4()
    raw_event = _build_event_bytes(basket_id=str(order_id))

    success = await handler.handle(raw_event)

    assert success is False
    handle_create_order.assert_awaited_once()


async def test_handler_skips_invalid_event() -> None:
    handle_create_order = AsyncMock()

    handler = BasketConfirmedIntegrationEventHandler(
        handle_create_order=handle_create_order,
    )

    success = await handler.handle(b"not a valid protobuf message")

    assert success is False
    handle_create_order.assert_not_awaited()


async def test_handler_skips_event_with_invalid_uuid() -> None:
    handle_create_order = AsyncMock()

    handler = BasketConfirmedIntegrationEventHandler(
        handle_create_order=handle_create_order,
    )

    raw_event = _build_event_bytes(basket_id="not-a-uuid")
    success = await handler.handle(raw_event)

    assert success is False
    handle_create_order.assert_not_awaited()


async def test_handler_skips_event_with_invalid_address() -> None:
    handle_create_order = AsyncMock()

    handler = BasketConfirmedIntegrationEventHandler(
        handle_create_order=handle_create_order,
    )

    raw_event = _build_event_bytes(
        basket_id=str(uuid4()),
        country="",
        city="",
        street="",
        house="",
        apartment="",
    )
    success = await handler.handle(raw_event)

    assert success is False
    handle_create_order.assert_not_awaited()
