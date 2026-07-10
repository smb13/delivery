from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from microarch.delivery.adapters.out.postgres.models import OutboxMessage
from microarch.delivery.adapters.out.postgres.outbox.job import OutboxJob
from microarch.delivery.adapters.out.postgres.outbox.mapper import OutboxMapper
from microarch.delivery.adapters.out.postgres.outbox.repository import OutboxRepository
from microarch.delivery.config.container import create_schema, drop_schema
from microarch.delivery.core.domain.model.location import Location
from microarch.delivery.core.domain.model.order.events import OrderCompletedDomainEvent
from microarch.delivery.core.domain.model.order.order import Order
from microarch.delivery.core.domain.model.volume import Volume
from microarch.delivery.core.ports.domain_event_publisher import IDomainEventPublisher

pytestmark = pytest.mark.asyncio


async def test_job_publishes_unprocessed_messages_and_marks_them_processed(
    engine,
) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    order_id = uuid4()
    order = Order.must_create(order_id, Location.must_create(5, 5), Volume.must_create(2))
    event = OrderCompletedDomainEvent(order_id)
    message = OutboxMapper.to_outbox_message(event, order)

    async with session_maker() as session:
        session.add(message)
        await session.commit()

    producer = AsyncMock(spec=IDomainEventPublisher)
    job = OutboxJob(session_maker, producer, OutboxRepository)
    await job.run()

    producer.publish.assert_awaited_once()
    published_event = producer.publish.await_args[0][0]
    assert isinstance(published_event, OrderCompletedDomainEvent)
    assert published_event.order_id == order_id
    assert published_event.event_id == event.event_id

    async with session_maker() as session:
        messages = list(
            (await session.execute(select(OutboxMessage))).scalars().all(),
        )

    assert len(messages) == 1
    assert messages[0].processed_on_utc is not None


async def test_job_keeps_message_unprocessed_when_publish_fails(engine) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    order_id = uuid4()
    order = Order.must_create(order_id, Location.must_create(5, 5), Volume.must_create(2))
    event = OrderCompletedDomainEvent(order_id)
    message = OutboxMapper.to_outbox_message(event, order)

    async with session_maker() as session:
        session.add(message)
        await session.commit()

    producer = AsyncMock(spec=IDomainEventPublisher)
    producer.publish.side_effect = RuntimeError("Kafka unavailable")
    job = OutboxJob(session_maker, producer, OutboxRepository)
    await job.run()

    async with session_maker() as session:
        messages = list(
            (await session.execute(select(OutboxMessage))).scalars().all(),
        )

    assert len(messages) == 1
    assert messages[0].processed_on_utc is None


async def test_job_skips_already_processed_messages(engine) -> None:
    await drop_schema(engine)
    await create_schema(engine)

    session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    order_id = uuid4()
    order = Order.must_create(order_id, Location.must_create(5, 5), Volume.must_create(2))
    event = OrderCompletedDomainEvent(order_id)
    message = OutboxMapper.to_outbox_message(event, order)
    message.mark_as_processed()

    async with session_maker() as session:
        session.add(message)
        await session.commit()

    producer = AsyncMock(spec=IDomainEventPublisher)
    job = OutboxJob(session_maker, producer, OutboxRepository)
    await job.run()

    producer.publish.assert_not_awaited()
