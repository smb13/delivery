from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from microarch.delivery.adapters.out.kafka import order_events_pb2
from microarch.delivery.adapters.out.kafka.order_events_producer import (
    OrderEventsKafkaProducer,
)
from microarch.delivery.core.domain.model.order.events import (
    OrderAssignedDomainEvent,
    OrderCompletedDomainEvent,
)

pytestmark = pytest.mark.asyncio


async def test_producer_serializes_order_assigned_event() -> None:
    kafka_producer = AsyncMock()
    producer = OrderEventsKafkaProducer(kafka_producer, topic="order.events")
    order_id = uuid4()

    await producer.publish(OrderAssignedDomainEvent(order_id))

    kafka_producer.send_and_wait.assert_awaited_once()
    call_args = kafka_producer.send_and_wait.await_args
    assert call_args.args[0] == "order.events"
    assert call_args.kwargs["key"] == str(order_id).encode()

    integration_event = order_events_pb2.OrderAssignedIntegrationEvent()
    integration_event.ParseFromString(call_args.kwargs["value"])
    assert integration_event.order_id == str(order_id)


async def test_producer_serializes_order_completed_event() -> None:
    kafka_producer = AsyncMock()
    producer = OrderEventsKafkaProducer(kafka_producer, topic="order.events")
    order_id = uuid4()

    await producer.publish(OrderCompletedDomainEvent(order_id))

    kafka_producer.send_and_wait.assert_awaited_once()
    call_args = kafka_producer.send_and_wait.await_args
    assert call_args.args[0] == "order.events"
    assert call_args.kwargs["key"] == str(order_id).encode()

    integration_event = order_events_pb2.OrderCompletedIntegrationEvent()
    integration_event.ParseFromString(call_args.kwargs["value"])
    assert integration_event.order_id == str(order_id)
