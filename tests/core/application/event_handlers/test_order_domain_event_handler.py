from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from microarch.delivery.adapters.out.kafka import order_events_pb2
from microarch.delivery.core.application.event_handlers import (
    OrderDomainEventHandler,
)
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)
from microarch.delivery.core.ports.integration_event_producer import (
    IIntegrationEventProducer,
)

pytestmark = pytest.mark.asyncio


async def test_handler_publishes_order_assigned_event() -> None:
    producer = AsyncMock(spec=IIntegrationEventProducer)
    handler = OrderDomainEventHandler(producer)
    order_id = uuid4()
    event = OrderAssignedDomainEvent(order_id)

    await handler.handle(event)

    producer.produce.assert_awaited_once()
    payload = producer.produce.await_args.kwargs["payload"]
    key = producer.produce.await_args.kwargs["key"]

    integration_event = order_events_pb2.OrderAssignedIntegrationEvent()
    integration_event.ParseFromString(payload)

    assert integration_event.order_id == str(order_id)
    assert key == str(order_id)


async def test_handler_publishes_order_completed_event() -> None:
    producer = AsyncMock(spec=IIntegrationEventProducer)
    handler = OrderDomainEventHandler(producer)
    order_id = uuid4()
    event = OrderCompletedDomainEvent(order_id)

    await handler.handle(event)

    producer.produce.assert_awaited_once()
    payload = producer.produce.await_args.kwargs["payload"]
    key = producer.produce.await_args.kwargs["key"]

    integration_event = order_events_pb2.OrderCompletedIntegrationEvent()
    integration_event.ParseFromString(payload)

    assert integration_event.order_id == str(order_id)
    assert key == str(order_id)
