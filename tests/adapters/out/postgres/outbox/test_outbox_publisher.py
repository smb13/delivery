from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from microarch.delivery.adapters.out.postgres.models import OutboxMessage
from microarch.delivery.adapters.out.postgres.outbox.publisher import (
    OutboxDomainEventPublisher,
)
from microarch.delivery.adapters.out.postgres.outbox.repository import OutboxRepository
from microarch.delivery.config.container import create_schema, drop_schema
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.volume import Volume

pytestmark = pytest.mark.asyncio


async def test_publisher_writes_domain_events_to_outbox(engine) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    order_id = uuid4()
    order = Order.must_create(order_id, Location.must_create(5, 5), Volume.must_create(2))
    order.assign()

    async with session_maker() as session:
        publisher = OutboxDomainEventPublisher(OutboxRepository(session))
        await publisher.publish([order])
        await session.commit()

    async with session_maker() as session:
        messages = list(
            (await session.execute(select(OutboxMessage))).scalars().all(),
        )

    assert len(messages) == 1
    assert messages[0].aggregate_id == str(order_id)
    assert messages[0].aggregate_type == "Order"
    assert "OrderAssignedDomainEvent" in messages[0].event_type
    assert messages[0].processed_on_utc is None


async def test_publisher_clears_domain_events_after_publishing(engine) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    order = Order.must_create(uuid4(), Location.must_create(5, 5), Volume.must_create(2))
    order.assign()

    async with session_maker() as session:
        publisher = OutboxDomainEventPublisher(OutboxRepository(session))
        await publisher.publish([order])

    assert len(order.get_domain_events()) == 0
