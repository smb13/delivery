from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from libs.errs.result import Result
from microarch.delivery.adapters.in_.kafka import (
    BasketConfirmedIntegrationEventHandler,
    basket_events_pb2,
)
from microarch.delivery.adapters.out.postgres.models import OrderModel
from microarch.delivery.config.container import create_schema, drop_schema
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.ports.geo_client import IGeoClient

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


async def test_handler_creates_order_from_basket_event(engine: AsyncEngine) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    geo_client = AsyncMock(spec=IGeoClient)
    geo_client.get_location.return_value = Result.success(Location.must_create(5, 5))

    handler = BasketConfirmedIntegrationEventHandler(
        session_factory=session_factory,
        geo_client=geo_client,
    )

    order_id = uuid4()
    raw_event = _build_event_bytes(basket_id=str(order_id))

    await handler.handle(raw_event)

    async with session_factory() as session:
        result = await session.execute(select(OrderModel).where(OrderModel.id == order_id))
        order_model = result.scalar_one_or_none()

    assert order_model is not None
    assert order_model.location_x == 5
    assert order_model.location_y == 5
    assert order_model.volume == 3


async def test_handler_skips_invalid_event(engine: AsyncEngine) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    geo_client = AsyncMock(spec=IGeoClient)

    handler = BasketConfirmedIntegrationEventHandler(
        session_factory=session_factory,
        geo_client=geo_client,
    )

    await handler.handle(b"not a valid protobuf message")

    async with session_factory() as session:
        result = await session.execute(select(OrderModel))
        orders = result.scalars().all()

    assert len(orders) == 0
    geo_client.get_location.assert_not_awaited()


async def test_handler_skips_event_with_invalid_uuid(engine: AsyncEngine) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    geo_client = AsyncMock(spec=IGeoClient)

    handler = BasketConfirmedIntegrationEventHandler(
        session_factory=session_factory,
        geo_client=geo_client,
    )

    raw_event = _build_event_bytes(basket_id="not-a-uuid")
    await handler.handle(raw_event)

    async with session_factory() as session:
        result = await session.execute(select(OrderModel))
        orders = result.scalars().all()

    assert len(orders) == 0
    geo_client.get_location.assert_not_awaited()
